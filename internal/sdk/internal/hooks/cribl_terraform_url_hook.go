package hooks

import (
	"fmt"
	"net/http"
	"net/url"
	"strings"
	"github.com/speakeasy/terraform-provider-criblio/internal/sdk/models/shared"
)

// CriblTerraformURLHook implements URL routing for Cribl Terraform API
type CriblTerraformURLHook struct {
	orgID       string
	workspaceID string
	serverURL   string
}

var (
	_ sdkInitHook       = (*CriblTerraformURLHook)(nil)
	_ beforeRequestHook = (*CriblTerraformURLHook)(nil)
)

// NewCriblTerraformURLHook creates a new URL hook for Cribl Terraform
func NewCriblTerraformURLHook() *CriblTerraformURLHook {
	hook := &CriblTerraformURLHook{}
	return hook
}

// SetServerURL sets the server URL for the hook
func (o *CriblTerraformURLHook) SetServerURL(url string) {
	o.serverURL = url
}

// SDKInit implements the sdkInitHook interface
func (o *CriblTerraformURLHook) SDKInit(baseURL string, client HTTPClient) (string, HTTPClient) {
	o.serverURL = baseURL
	return baseURL, client
}

// BeforeRequest implements the beforeRequestHook interface
// It updates the request URL with organization and workspace IDs
func (o *CriblTerraformURLHook) BeforeRequest(ctx BeforeRequestContext, req *http.Request) (*http.Request, error) {
	// Get org and workspace IDs from security source
	if ctx.SecuritySource != nil {
		if security, err := ctx.SecuritySource(ctx.Context); err == nil {
			if s, ok := security.(shared.Security); ok {
				if s.OrganizationID != nil {
					o.orgID = *s.OrganizationID
				}
				if s.WorkspaceID != nil {
					o.workspaceID = *s.WorkspaceID
				}
			}
		}
	}

	serverURL := strings.TrimRight(o.serverURL, "/")
	path := strings.TrimLeft(req.URL.Path, "/")

	newURL := fmt.Sprintf("%s/organizations/%s/workspaces/%s/app/api/v1/%s",
		serverURL,
		o.orgID,
		o.workspaceID,
		path,
	)

	parsedURL, err := url.Parse(newURL)
	if err != nil {
		return req, err
	}

	req.URL = parsedURL
	return req, nil
}