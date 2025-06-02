package hooks

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"net/url"
	"os"
	"strings"
	"sync"
	"time"
	"github.com/speakeasy/terraform-provider-criblio/internal/sdk/models/shared"
)

type TokenInfo struct {
	Token     string
	ExpiresAt time.Time
}

type CriblTerraformAuthHook struct {
	client   HTTPClient
	sessions sync.Map
	baseURL  string
}

var (
	_ sdkInitHook       = (*CriblTerraformAuthHook)(nil)
	_ beforeRequestHook = (*CriblTerraformAuthHook)(nil)
)

func NewCriblTerraformAuthHook() *CriblTerraformAuthHook {
	return &CriblTerraformAuthHook{}
}

func (o *CriblTerraformAuthHook) SDKInit(baseURL string, client HTTPClient) (string, HTTPClient) {
	o.client = client
	o.baseURL = baseURL
	return baseURL, client
}

func (o *CriblTerraformAuthHook) BeforeRequest(ctx BeforeRequestContext, req *http.Request) (*http.Request, error) {
	// Check for bearer token in environment variable
	if bearerToken := os.Getenv("CRIBL_BEARER_TOKEN"); bearerToken != "" {
		req.Header.Set("Authorization", "Bearer "+bearerToken)
		return req, nil
	}

	// Get credentials from config or environment
	config, err := GetCredentials()
	if err != nil {
		log.Printf("[ERROR] Failed to get credentials: %v", err)
		return req, nil
	}

	if config != nil {
		// Get audience from base URL
		audience := ""
		if o.baseURL != "" {
			// Replace "app" with "api" in the base URL
			audience = strings.Replace(o.baseURL, "app.", "api.", 1)
		} else if os.Getenv("CRIBL_AUDIENCE") != "" {
			audience = os.Getenv("CRIBL_AUDIENCE")
		} else {
			log.Printf("[ERROR] No base URL or audience provided")
			return req, fmt.Errorf("no base URL or audience provided")
		}

		// Get or create session
		sessionKey := fmt.Sprintf("%s:%s", config.ClientID, config.ClientSecret)
		var tokenInfo *TokenInfo
		
		if cachedTokenInfo, ok := o.sessions.Load(sessionKey); ok {
			tokenInfo = cachedTokenInfo.(*TokenInfo)
			// Check if token is expired or about to expire (within 60 minutes)
			if time.Until(tokenInfo.ExpiresAt) < 60*time.Minute {
				tokenInfo = nil
			}
		}

		if tokenInfo == nil {
			// Get new token
			newTokenInfo, err := o.getBearerToken(ctx.Context, config.ClientID, config.ClientSecret, audience)
			if err != nil {
				log.Printf("[ERROR] Failed to get bearer token: %v", err)
				return req, err
			}
			tokenInfo = newTokenInfo
			o.sessions.Store(sessionKey, tokenInfo)
		}

		req.Header.Set("Authorization", "Bearer "+tokenInfo.Token)

		// Set security information with organization and workspace IDs
		if ctx.SecuritySource != nil {
			// Create local copies to ensure they're not nil
			orgID := config.OrganizationID
			workspaceID := config.Workspace

			// Create security object with the values
			security := shared.Security{
				OrganizationID: &orgID,
				WorkspaceID:    &workspaceID,
			}

			// Set the security source
			ctx.SecuritySource = func(context.Context) (interface{}, error) {
				return security, nil
			}
		}
	}

	return req, nil
}

func (o *CriblTerraformAuthHook) getBearerToken(ctx context.Context, clientID, clientSecret, audience string) (*TokenInfo, error) {
	// Get auth URL from base URL
	authURL := ""
	if o.baseURL != "" {
		// Replace "app" with "login" in the base URL and append /oauth/token
		authURL = strings.Replace(o.baseURL, "app.", "login.", 1)
		authURL = strings.TrimSuffix(authURL, "/")
		authURL = authURL + "/oauth/token"
	} else {
		log.Printf("[ERROR] No base URL provided")
		return nil, fmt.Errorf("no base URL provided")
	}
	
	// Create form data
	formData := url.Values{}
	formData.Set("grant_type", "client_credentials")
	formData.Set("client_id", clientID)
	formData.Set("client_secret", clientSecret)
	formData.Set("audience", audience)

	req, err := http.NewRequestWithContext(ctx, "POST", authURL, strings.NewReader(formData.Encode()))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %v", err)
	}
	req.Header.Set("Content-Type", "application/x-www-form-urlencoded")

	resp, err := o.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to make request: %v", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("failed to read response: %v", err)
	}

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("failed to get token: %s", string(body))
	}

	var result struct {
		AccessToken string `json:"access_token"`
		ExpiresIn   int    `json:"expires_in"`
	}
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("failed to parse response: %v", err)
	}

	// Calculate expiration time
	expiresAt := time.Now().Add(time.Duration(result.ExpiresIn) * time.Second)

	return &TokenInfo{
		Token:     result.AccessToken,
		ExpiresAt: expiresAt,
	}, nil
}