#!/bin/bash
# PostgreSQL Setup Script for Glam by Lynn
# This script requires sudo privileges to set up PostgreSQL

set -e  # Exit on error

echo "=== Glam by Lynn PostgreSQL Setup ==="
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Database configuration
DB_USER="${DB_USER:-glam_user}"
DB_PASSWORD="${DB_PASSWORD:-glam_password_dev}"
DB_NAME="${DB_NAME:-glam_by_lynn}"
DB_TEST_NAME="${DB_TEST_NAME:-glam_by_lynn_test}"

echo -e "${YELLOW}Creating PostgreSQL user and databases...${NC}"
echo "User: $DB_USER"
echo "Development DB: $DB_NAME"
echo "Test DB: $DB_TEST_NAME"
echo

# Create PostgreSQL user and databases
sudo -u postgres psql <<EOF
-- Create user if not exists
DO \$\$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_user WHERE usename = '$DB_USER') THEN
    CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';
  END IF;
END
\$\$;

-- Create development database
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME OWNER $DB_USER;

-- Create test database
DROP DATABASE IF EXISTS $DB_TEST_NAME;
CREATE DATABASE $DB_TEST_NAME OWNER $DB_USER;

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL PRIVILEGES ON DATABASE $DB_TEST_NAME TO $DB_USER;

\c $DB_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;

\c $DB_TEST_NAME
GRANT ALL ON SCHEMA public TO $DB_USER;
EOF

if [ $? -eq 0 ]; then
  echo -e "${GREEN}✓ PostgreSQL setup completed successfully!${NC}"
  echo
  echo "Database credentials:"
  echo "  User: $DB_USER"
  echo "  Password: $DB_PASSWORD"
  echo "  Development DB: $DB_NAME"
  echo "  Test DB: $DB_TEST_NAME"
  echo
  echo "Add this to your .env file:"
  echo "  DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_NAME"
  echo
  echo "Add this to your environment for tests:"
  echo "  TEST_DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@localhost:5432/$DB_TEST_NAME"
else
  echo -e "${RED}✗ PostgreSQL setup failed${NC}"
  exit 1
fi
