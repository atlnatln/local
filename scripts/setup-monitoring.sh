#!/bin/bash
# ============================================================================
# Monitoring Setup Script  
# Deploys Prometheus + Grafana monitoring stack
# ============================================================================

set -euo pipefail

echo "🔍 Setting up VPS monitoring dashboard..."

# Create monitoring directories
mkdir -p infrastructure/monitoring/{prometheus/{rules,data},grafana/{provisioning/{datasources,dashboards},dashboards,data}}

# Create Grafana datasource configuration
cat > infrastructure/monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1
datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: false
    jsonData:
      timeInterval: "30s"
EOF

# Create Grafana dashboard configuration
cat > infrastructure/monitoring/grafana/provisioning/dashboards/default.yml << 'EOF'
apiVersion: 1
providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 30
    options:
      path: /var/lib/grafana/dashboards
EOF

# Download popular dashboard templates
echo "📊 Downloading Grafana dashboard templates..."
curl -s https://grafana.com/api/dashboards/1860/revisions/37/download > infrastructure/monitoring/grafana/dashboards/node-exporter.json
curl -s https://grafana.com/api/dashboards/193/revisions/4/download > infrastructure/monitoring/grafana/dashboards/cadvisor.json
curl -s https://grafana.com/api/dashboards/12559/revisions/1/download > infrastructure/monitoring/grafana/dashboards/nginx.json

# Create basic alerting rules
cat > infrastructure/monitoring/prometheus/rules/alerts.yml << 'EOF'
groups:
  - name: system_alerts
    rules:
      - alert: HighCpuUsage
        expr: 100 - (avg by(instance) (irate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage detected"
          description: "CPU usage is above 80% for 5 minutes"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes * 100 > 90
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High memory usage detected"
          description: "Memory usage is above 90% for 5 minutes"

      - alert: DiskSpaceLow
        expr: (node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"}) * 100 < 10
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Low disk space"
          description: "Disk space is below 10%"
EOF

# Add nginx status endpoint to main nginx config
echo "🔧 Adding nginx status endpoint..."
if ! grep -q "location /nginx_status" infrastructure/nginx/nginx.conf; then
    cat >> infrastructure/nginx/nginx.conf << 'EOF'

    # Nginx status endpoint for monitoring (added by monitoring setup)
    server {
        listen 8080;
        server_name localhost;
        
        location /nginx_status {
            stub_status on;
            access_log off;
            allow 127.0.0.1;
            allow 10.0.0.0/8;
            allow 172.16.0.0/12;
            allow 192.168.0.0/16;
            deny all;
        }
        
        location /health {
            access_log off;
            return 200 "OK\n";
            add_header Content-Type text/plain;
        }
    }
EOF
fi

# Set permissions
sudo chown -R 472:472 infrastructure/monitoring/grafana/data 2>/dev/null || true
sudo chmod 755 infrastructure/monitoring/prometheus/data 2>/dev/null || true

echo "✅ Monitoring setup complete!"
echo ""
echo "📊 To start monitoring:"
echo "  cd infrastructure && docker-compose -f monitoring-compose.yml up -d"
echo ""
echo "🌐 Access dashboards:"
echo "  Grafana: http://localhost:3001 (admin/webimar2024!)"
echo "  Prometheus: http://localhost:9090"
echo "  Node metrics: http://localhost:9100"
echo ""
echo "⚠️  Remember to:"
echo "  1. Change default Grafana password"
echo "  2. Configure email/Slack alerts"
echo "  3. Set up log aggregation with ELK stack"