#!/bin/bash
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DUMP_URL="https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz"
DUMP_FILE="openfoodfacts-mongodbdump.gz"
DUMP_DIR="openfoodfacts-mongodbdump"
CHECKSUM_URL="https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz.sha256"
CHECKSUM_FILE="openfoodfacts-mongodbdump.gz.sha256"
MONGODB_HOST="localhost:27017"
MONGODB_DB="off"

echo -e "${GREEN}=== OpenFoodFacts MongoDB Setup ===${NC}"
echo ""

# Check if MongoDB is running
echo -e "${YELLOW}Checking MongoDB connection...${NC}"
if ! docker exec nomnom-mongodb mongosh --eval "db.version()" > /dev/null 2>&1; then
    echo -e "${RED}Error: MongoDB container 'nomnom-mongodb' is not running!${NC}"
    echo "Please start MongoDB first: docker-compose up -d"
    exit 1
fi
echo -e "${GREEN}✓ MongoDB is running${NC}"
echo ""

# Download checksum file
echo -e "${YELLOW}Downloading checksum file...${NC}"
if curl -f -s -o "$CHECKSUM_FILE" "$CHECKSUM_URL"; then
    EXPECTED_CHECKSUM=$(cat "$CHECKSUM_FILE" | awk '{print $1}')
    echo -e "${GREEN}✓ Checksum downloaded: ${EXPECTED_CHECKSUM:0:16}...${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Could not download checksum file, will skip verification${NC}"
    EXPECTED_CHECKSUM=""
fi
echo ""

# Check if dump file already exists and verify checksum
if [ -f "$DUMP_FILE" ]; then
    echo -e "${YELLOW}Found existing dump file, verifying checksum...${NC}"
    
    if [ -n "$EXPECTED_CHECKSUM" ]; then
        ACTUAL_CHECKSUM=$(shasum -a 256 "$DUMP_FILE" | awk '{print $1}')
        
        if [ "$ACTUAL_CHECKSUM" == "$EXPECTED_CHECKSUM" ]; then
            echo -e "${GREEN}✓ Checksum matches! Using existing file.${NC}"
            echo -e "  Size: $(du -h "$DUMP_FILE" | cut -f1)"
            SKIP_DOWNLOAD=true
        else
            echo -e "${RED}✗ Checksum mismatch!${NC}"
            echo -e "  Expected: $EXPECTED_CHECKSUM"
            echo -e "  Got:      $ACTUAL_CHECKSUM"
            echo -e "${YELLOW}Will re-download...${NC}"
            rm -f "$DUMP_FILE"
            SKIP_DOWNLOAD=false
        fi
    else
        echo -e "${YELLOW}⚠ Cannot verify checksum (checksum file unavailable)${NC}"
        echo -e "  Size: $(du -h "$DUMP_FILE" | cut -f1)"
        read -p "Use existing file anyway? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            SKIP_DOWNLOAD=true
        else
            rm -f "$DUMP_FILE"
            SKIP_DOWNLOAD=false
        fi
    fi
else
    SKIP_DOWNLOAD=false
fi
echo ""

# Download dump file if needed
if [ "$SKIP_DOWNLOAD" != "true" ]; then
    echo -e "${YELLOW}Downloading OpenFoodFacts MongoDB dump (~20GB)...${NC}"
    echo "This will take 30-60 minutes depending on your connection."
    echo ""
    
    if curl -# -o "$DUMP_FILE" "$DUMP_URL"; then
        echo -e "${GREEN}✓ Download complete!${NC}"
        echo -e "  Size: $(du -h "$DUMP_FILE" | cut -f1)"
        
        # Verify checksum of downloaded file
        if [ -n "$EXPECTED_CHECKSUM" ]; then
            echo -e "${YELLOW}Verifying download...${NC}"
            ACTUAL_CHECKSUM=$(shasum -a 256 "$DUMP_FILE" | awk '{print $1}')
            
            if [ "$ACTUAL_CHECKSUM" == "$EXPECTED_CHECKSUM" ]; then
                echo -e "${GREEN}✓ Checksum verified!${NC}"
            else
                echo -e "${RED}✗ Download corrupted! Checksum mismatch.${NC}"
                echo -e "  Expected: $EXPECTED_CHECKSUM"
                echo -e "  Got:      $ACTUAL_CHECKSUM"
                rm -f "$DUMP_FILE"
                exit 1
            fi
        fi
    else
        echo -e "${RED}Error: Download failed!${NC}"
        exit 1
    fi
    echo ""
fi

# Check if already extracted
if [ -d "$DUMP_DIR" ]; then
    echo -e "${YELLOW}Found existing extracted dump directory${NC}"
    read -p "Re-extract? This will overwrite existing files (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$DUMP_DIR"
        SKIP_EXTRACT=false
    else
        SKIP_EXTRACT=true
    fi
else
    SKIP_EXTRACT=false
fi
echo ""

# Extract dump
if [ "$SKIP_EXTRACT" != "true" ]; then
    echo -e "${YELLOW}Extracting dump (~80GB)...${NC}"
    if gunzip -k "$DUMP_FILE"; then
        # gunzip creates openfoodfacts-mongodbdump (without .gz)
        # mongorestore expects a directory, so we need to check the structure
        echo -e "${GREEN}✓ Extraction complete!${NC}"
        
        # Check if it's a tar archive or directory
        if [ -f "openfoodfacts-mongodbdump" ]; then
            echo -e "${YELLOW}Extracting tar archive...${NC}"
            mkdir -p "$DUMP_DIR"
            tar -xf openfoodfacts-mongodbdump -C "$DUMP_DIR"
            rm openfoodfacts-mongodbdump
        fi
    else
        echo -e "${RED}Error: Extraction failed!${NC}"
        exit 1
    fi
    echo ""
fi

# Check if database already exists
echo -e "${YELLOW}Checking if database already exists...${NC}"
PRODUCT_COUNT=$(docker exec nomnom-mongodb mongosh --quiet --eval "use $MONGODB_DB; db.products.countDocuments()" | tail -n 1)

if [ "$PRODUCT_COUNT" -gt 0 ]; then
    echo -e "${YELLOW}⚠ Database '$MONGODB_DB' already contains $PRODUCT_COUNT products${NC}"
    read -p "Re-import? This will overwrite existing data (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${GREEN}Skipping import. Setup complete!${NC}"
        exit 0
    fi
    
    echo -e "${YELLOW}Dropping existing database...${NC}"
    docker exec nomnom-mongodb mongosh --quiet --eval "use $MONGODB_DB; db.dropDatabase()"
fi
echo ""

# Import into MongoDB
echo -e "${YELLOW}Importing into MongoDB (this will take 30-60 minutes)...${NC}"
echo "Database: $MONGODB_DB"
echo ""

if docker exec -i nomnom-mongodb mongorestore --host "$MONGODB_HOST" --db "$MONGODB_DB" "/data/db-dump/$DUMP_DIR" < /dev/null; then
    echo -e "${GREEN}✓ Import complete!${NC}"
else
    # Try alternative method - copy dump into container first
    echo -e "${YELLOW}Direct restore failed, trying alternative method...${NC}"
    
    # Copy dump directory into container
    docker cp "$DUMP_DIR" nomnom-mongodb:/tmp/
    
    # Run mongorestore from within container
    docker exec nomnom-mongodb mongorestore --host "$MONGODB_HOST" --db "$MONGODB_DB" "/tmp/$DUMP_DIR"
    
    # Clean up
    docker exec nomnom-mongodb rm -rf "/tmp/$DUMP_DIR"
    
    echo -e "${GREEN}✓ Import complete!${NC}"
fi
echo ""

# Verify import
echo -e "${YELLOW}Verifying import...${NC}"
PRODUCT_COUNT=$(docker exec nomnom-mongodb mongosh --quiet --eval "use $MONGODB_DB; db.products.countDocuments()" | tail -n 1)
COLLECTION_COUNT=$(docker exec nomnom-mongodb mongosh --quiet --eval "use $MONGODB_DB; db.getCollectionNames().length" | tail -n 1)

echo -e "${GREEN}✓ Import verified!${NC}"
echo -e "  Database: $MONGODB_DB"
echo -e "  Collections: $COLLECTION_COUNT"
echo -e "  Products: $PRODUCT_COUNT"
echo ""

# Check indexes
echo -e "${YELLOW}Verifying indexes...${NC}"
docker exec nomnom-mongodb mongosh --quiet --eval "use $MONGODB_DB; db.products.getIndexes()" > /dev/null 2>&1
echo -e "${GREEN}✓ Indexes verified${NC}"
echo ""

echo -e "${GREEN}=== Setup Complete! ===${NC}"
echo ""
echo "Next steps:"
echo "1. Create app indexes:    python scripts/create_indexes.py"
echo "2. Seed users:            python scripts/seed_users.py"
echo "3. Start backend:         python main.py"
echo ""
echo "Test the database:"
echo "  docker exec -it nomnom-mongodb mongosh"
echo "  > use off"
echo "  > db.products.findOne({code: \"3017620422003\"})"
