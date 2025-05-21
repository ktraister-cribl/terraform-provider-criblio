# terraform-provider-criblio

A Terraform provider for managing Cribl resources.

## Requirements

- [Terraform](https://www.terraform.io/downloads.html) >= 1.0
- [Go](https://golang.org/doc/install) >= 1.19

## Installation

To install this provider, copy and paste this code into your Terraform configuration. Then, run `terraform init`.

```hcl
terraform {
  required_providers {
    criblio = {
      source  = "criblio/criblio"
    }
  }
}

provider "criblio" {
  # Configuration options
}
```

## Authentication

The Cribl provider supports multiple authentication methods. You can configure authentication using environment variables, credentials file, or directly in the provider configuration block.

### Environment Variables

You can set the following environment variables:

```bash
# Direct authentication
export CRIBL_BEARER_TOKEN="your-bearer-token"

# OAuth authentication
export CRIBL_CLIENT_ID="your-client-id"
export CRIBL_CLIENT_SECRET="your-client-secret"
export CRIBL_ORGANIZATION_ID="your-organization-id"
export CRIBL_WORKSPACE_ID="your-workspace-id"
```

### Credentials File

You can store your credentials in `~/.cribl/credentials` or `~/.cribl` (legacy) with the following format:

```ini
[default]
client_id = your-client-id
client_secret = your-client-secret
organization_id = your-organization-id
workspace = your-workspace-id

[profile2]
client_id = another-client-id
client_secret = another-client-secret
organization_id = another-organization-id
workspace = another-workspace-id
```

To use a specific profile, set the `CRIBL_PROFILE` environment variable:

```bash
export CRIBL_PROFILE="profile2"
```

### Provider Configuration

You can also configure authentication directly in your Terraform configuration:

```hcl
provider "criblio" {
  # Using bearer token
  bearer_token = "your-bearer-token"

  # Or using OAuth credentials
  client_id        = "your-client-id"
  client_secret    = "your-client-secret"
  organization_id  = "your-organization-id"
  workspace_id     = "your-workspace-id"
}
```

### Authentication Methods

#### 1. Bearer Token

The simplest way to authenticate is using a bearer token:

```hcl
provider "criblio" {
  bearer_token = "your-bearer-token"
}
```

#### 2. OAuth Authentication (Recommended)

For OAuth authentication, you can use client credentials:

```hcl
provider "criblio" {
  client_id       = "your-client-id"
  client_secret   = "your-client-secret"
  organization_id = "your-organization-id"
  workspace_id    = "your-workspace-id"
}
```

### Example with Environment Variables

```hcl
# main.tf
provider "criblio" {
  # Credentials will be read from environment variables
  url = "https://your-cribl-instance:9000"
}

# Use the provider
resource "criblio_pipeline" "example" {
  name = "example-pipeline"
  # ... other configuration
}
```

```bash
# Set environment variables
export CRIBL_CLIENT_ID="your-client-id"
export CRIBL_CLIENT_SECRET="your-client-secret"
export CRIBL_ORGANIZATION_ID="your-organization-id"
export CRIBL_WORKSPACE_ID="your-workspace-id"

# Run Terraform
terraform init
terraform plan
```

## Available Resources and Data Sources

### Resources

* [criblio_destination](docs/resources/destination.md) - Manage Cribl destinations
* [criblio_group](docs/resources/group.md) - Manage Cribl groups
* [criblio_pack](docs/resources/pack.md) - Manage Cribl packs
* [criblio_pack_pipeline](docs/resources/pack_pipeline.md) - Manage Cribl pack pipelines
* [criblio_pipeline](docs/resources/pipeline.md) - Manage Cribl pipelines
* [criblio_source](docs/resources/source.md) - Manage Cribl sources

### Data Sources

* [criblio_pack](docs/data-sources/pack.md) - Query Cribl packs
* [criblio_pack_pipeline](docs/data-sources/pack_pipeline.md) - Query Cribl pack pipelines
* [criblio_pipeline](docs/data-sources/pipeline.md) - Query Cribl pipelines

## Development

### Local Testing

#### Using Local Provider

To validate changes locally, you can use the `--debug` flag to execute the provider against a terraform instance locally. This also allows for debuggers (e.g. delve) to be attached to the provider.

```sh
go run main.go --debug
# Copy the TF_REATTACH_PROVIDERS env var
# In a new terminal
cd examples/your-example
TF_REATTACH_PROVIDERS=... terraform init
TF_REATTACH_PROVIDERS=... terraform apply
```

#### Using Compiled Provider

You can use local provider builds by setting a `dev_overrides` block in a configuration file called `.terraformrc`. This block overrides all other configured installation methods.

1. Execute `go build` to construct a binary called `terraform-provider-criblio`
2. Configure `.terraformrc` in your home directory with a `dev_overrides` section:

```hcl
provider_installation {
  dev_overrides {
    "registry.terraform.io/criblio/criblio" = "<PATH>"
  }

  # For all other providers, install them directly from their origin provider
  # registries as normal. If you omit this, Terraform will _only_ use
  # the dev_overrides block, and so no other providers will be available.
  direct {}
}
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the terms of the license included in the repository.

<!-- Start Summary [summary] -->
## Summary


<!-- End Summary [summary] -->

<!-- Start Table of Contents [toc] -->
## Table of Contents
<!-- $toc-max-depth=2 -->
* [terraform-provider-criblio](#terraform-provider-criblio)
  * [Requirements](#requirements)
  * [Installation](#installation)
  * [Authentication](#authentication)
  * [Available Resources and Data Sources](#available-resources-and-data-sources)
  * [Development](#development)
  * [Contributing](#contributing)
  * [License](#license)
  * [Installation](#installation-1)
  * [Available Resources and Data Sources](#available-resources-and-data-sources-1)
  * [Testing the provider locally](#testing-the-provider-locally)

<!-- End Table of Contents [toc] -->

<!-- Start Installation [installation] -->
## Installation

To install this provider, copy and paste this code into your Terraform configuration. Then, run `terraform init`.

```hcl
terraform {
  required_providers {
    criblio = {
      source  = "speakeasy/criblio"
      version = "1.0.0"
    }
  }
}

provider "criblio" {
  # Configuration options
}
```
<!-- End Installation [installation] -->

<!-- Start Available Resources and Data Sources [operations] -->
## Available Resources and Data Sources

### Resources

* [criblio_destination](docs/resources/destination.md)
* [criblio_group](docs/resources/group.md)
* [criblio_pack](docs/resources/pack.md)
* [criblio_pack_pipeline](docs/resources/pack_pipeline.md)
* [criblio_pipeline](docs/resources/pipeline.md)
* [criblio_source](docs/resources/source.md)
### Data Sources

* [criblio_pack](docs/data-sources/pack.md)
* [criblio_pack_pipeline](docs/data-sources/pack_pipeline.md)
* [criblio_pipeline](docs/data-sources/pipeline.md)
<!-- End Available Resources and Data Sources [operations] -->

<!-- Start Testing the provider locally [usage] -->
## Testing the provider locally

#### Local Provider

Should you want to validate a change locally, the `--debug` flag allows you to execute the provider against a terraform instance locally.

This also allows for debuggers (e.g. delve) to be attached to the provider.

```sh
go run main.go --debug
# Copy the TF_REATTACH_PROVIDERS env var
# In a new terminal
cd examples/your-example
TF_REATTACH_PROVIDERS=... terraform init
TF_REATTACH_PROVIDERS=... terraform apply
```

#### Compiled Provider

Terraform allows you to use local provider builds by setting a `dev_overrides` block in a configuration file called `.terraformrc`. This block overrides all other configured installation methods.

1. Execute `go build` to construct a binary called `terraform-provider-criblio`
2. Ensure that the `.terraformrc` file is configured with a `dev_overrides` section such that your local copy of terraform can see the provider binary

Terraform searches for the `.terraformrc` file in your home directory and applies any configuration settings you set.

```
provider_installation {

  dev_overrides {
      "registry.terraform.io/speakeasy/criblio" = "<PATH>"
  }

  # For all other providers, install them directly from their origin provider
  # registries as normal. If you omit this, Terraform will _only_ use
  # the dev_overrides block, and so no other providers will be available.
  direct {}
}
```
<!-- End Testing the provider locally [usage] -->

<!-- Placeholder for Future Speakeasy SDK Sections -->
