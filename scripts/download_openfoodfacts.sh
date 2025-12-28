#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Configuration
DUMP_URL="https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz"
DUMP_FILE="openfoodfacts-mongodbdump.gz"
CHECKSUM_URL="https://static.openfoodfacts.org/data/openfoodfacts-mongodbdump.gz.sha256"
CHECKSUM_FILE="openfoodfacts-mongodbdump.gz.sha256"

echo -e "${GREEN}=== OpenFoodFacts Download ===${NC}"
echo ""

# Download checksum
echo -e "${YELLOW}Downloading checksum...${NC}"
if curl -f -s -L -o "$CHECKSUM_FILE" "$CHECKSUM_URL"; then
    EXPECTED_CHECKSUM=$(cat "$CHECKSUM_FILE" | awk '{print $1}')
    echo -e "${GREEN}✓ Expected checksum: ${EXPECTED_CHECKSUM:0:16}...${NC}"
else
    echo -e "${YELLOW}⚠ Could not download checksum${NC}"
    EXPECTED_CHECKSUM=""
fi
echo ""

# Check existing file
if [ -f "$DUMP_FILE" ]; then
    echo -e "${YELLOW}Found existing file, verifying...${NC}"
    
    if [ -n "$EXPECTED_CHECKSUM" ]; then
        ACTUAL_CHECKSUM=$(shasum -a 256 "$DUMP_FILE" | awk '{print $1}')
        
        if [ "$ACTUAL_CHECKSUM" == "$EXPECTED_CHECKSUM" ]; then
            echo -e "${GREEN}✓ Checksum matches! File is up to date.${NC}"
            echo -e "  Size: $(du -h "$DUMP_FILE" | cut -f1)"
            exit 0
        else
            echo -e "${RED}✗ Checksum mismatch, re-downloading...${NC}"
            rm -f "$DUMP_FILE"
        fi
    else
        echo -e "${YELLOW}⚠ Cannot verify (no checksum available)${NC}"
        read -p "Re-download anyway? (y/N) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 0
        fi
        rm -f "$DUMP_FILE"
    fi
fi

# Download
echo -e "${YELLOW}Downloading OpenFoodFacts dump (~20GB)...${NC}"
echo "This may take 30-60 minutes."
echo ""

if curl -# -L -o "$DUMP_FILE" "$DUMP_URL"; then
    echo ""
    echo -e "${GREEN}✓ Download complete!${NC}"
    echo -e "  Size: $(du -h "$DUMP_FILE" | cut -f1)"
    
    # Verify
    if [ -n "$EXPECTED_CHECKSUM" ]; then
        echo -e "${YELLOW}Verifying checksum...${NC}"
        ACTUAL_CHECKSUM=$(shasum -a 256 "$DUMP_FILE" | awk '{print $1}')
        
        if [ "$ACTUAL_CHECKSUM" == "$EXPECTED_CHECKSUM" ]; then
            echo -e "${GREEN}✓ Verified!${NC}"
        else
            echo -e "${RED}✗ Checksum mismatch!${NC}"
            echo -e "  Expected: $EXPECTED_CHECKSUM"
            echo -e "  Got:      $ACTUAL_CHECKSUM"
            exit 1
        fi
    fi
else
    echo -e "${RED}Download failed!${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}Download complete! Run setup script to import:${NC}"
echo "  ./scripts/setup_mongodb.sh"
