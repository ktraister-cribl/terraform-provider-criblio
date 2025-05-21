# Syslog to Cribl Lake Example

This example demonstrates how to set up a complete syslog data pipeline using Cribl Stream, from syslog ingestion to Cribl Lake storage.

## Architecture

The setup consists of four main components:

1. **Worker Group**: A dedicated worker group for handling syslog data
2. **Syslog Source**: A syslog input source listening on port 20005
3. **Cribl Lake Destination**: A destination configured to store data in Cribl Lake
4. **Processing Pack**: A pack for processing syslog data before storage

## Configuration Details

### Worker Group
- ID: `syslog-workers`
- Single worker configuration
- On-premises deployment
- Stream product type

### Syslog Source
- Listens on port 20005 (TCP/UDP)
- Accepts connections from any IP (0.0.0.0)
- Includes persistent queue configuration for reliability
- TLS disabled by default
- Connected to the Cribl Lake destination

### Cribl Lake Destination
- Stores data in JSON format
- Uses gzip compression
- Includes dead-letter queue configuration
- Configures file size limits and backpressure handling

### Processing Pack
- ID: `syslog-processing`
- Requires a pack file (`syslog-processing.crbl`)

## Prerequisites

1. Cribl Stream instance with appropriate permissions
2. Access to Cribl Lake
3. The syslog processing pack file (`syslog-processing.crbl`)

## Usage

1. Place your syslog processing pack file in the same directory as `main.tf`
2. Update the provider configuration with your organization and workspace IDs:
   ```hcl
   provider "cribl-terraform" {
     organization_id = "your-org-id"
     workspace_id = "your-workspace-id"
   }
   ```
3. Initialize Terraform:
   ```bash
   terraform init
   ```
4. Apply the configuration:
   ```bash
   terraform apply
   ```

## Outputs

The configuration provides the following outputs:
- Worker group details
- Source details
- Destination details
- Pack details

## Notes

- The syslog source is configured to listen on port 20005. Make sure this port is available and accessible.
- The Cribl Lake destination uses default settings for file handling and compression.
- The configuration includes persistent queue settings for reliability.
- TLS is disabled by default but can be enabled by modifying the TLS configuration in the source.

## Customization

You can customize this setup by:
1. Modifying the port numbers in the syslog source
2. Adjusting the file size limits and backpressure settings
3. Enabling TLS for secure syslog transmission
4. Modifying the Cribl Lake destination path and format settings
5. Adding additional processing steps in the pack 