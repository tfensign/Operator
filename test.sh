#!/bin/bash

BASE="http://localhost:3001"

echo "=== Testing Operator API ==="
echo ""

echo "1. Setup Master Password"
curl -s -X POST $BASE/auth/setup \
  -H "Content-Type: application/json" \
  -d '{"master_password":"testpass123"}' | jq .

echo ""
echo "2. Check Initialized"
curl -s $BASE/auth/initialized | jq .

echo ""
echo "3. Send Email Message (High Priority - URGENT keyword)"
curl -s -X POST $BASE/webhook/email \
  -H "Content-Type: application/json" \
  -d '{"from_address":"boss@company.com","subject":"URGENT: Action Required","body":"TODO: Review report\nTODO: Send feedback"}' | jq .

echo ""
echo "4. Send Slack Message (Normal Priority)"
curl -s -X POST $BASE/webhook/slack \
  -H "Content-Type: application/json" \
  -d '{"from_address":"john@company.com","subject":"Team Update","body":"Status update for the team"}' | jq .

echo ""
echo "5. Send SMS Message (Low Priority)"
curl -s -X POST $BASE/webhook/sms \
  -H "Content-Type: application/json" \
  -d '{"from_address":"+1-555-0100","subject":"(SMS)","body":"Hey, just checking in"}' | jq .

echo ""
echo "6. Get All Messages (sorted by priority)"
echo "Messages:"
curl -s $BASE/messages | jq '.[] | {id, platform, from_address, subject, priority}'

echo ""
echo "7. Filter Email Only"
curl -s "$BASE/messages?platform=email" | jq '.[] | {id, from_address, priority}'

echo ""
echo "8. Search for TODO items"
curl -s -X POST $BASE/messages/search \
  -H "Content-Type: application/json" \
  -d '{"query_text":"TODO"}' | jq '.[] | {id, subject, body}'

echo ""
echo "9. Get Single Message (ID 1)"
curl -s $BASE/messages/1 | jq .

echo ""
echo "10. Mark Message as Read"
curl -s -X PATCH $BASE/messages/1 \
  -H "Content-Type: application/json" \
  -d "{\"read_at\":\"$(date -u +'%Y-%m-%dT%H:%M:%S')\"}" | jq .

echo ""
echo "11. Create New Checklist"
CHECKLIST=$(curl -s -X POST $BASE/checklists \
  -H "Content-Type: application/json" \
  -d '{"title":"Q4 Tasks","description":"Important items for Q4"}')
echo $CHECKLIST | jq .
CHECKLIST_ID=$(echo $CHECKLIST | jq .id)

echo ""
echo "12. Create Checklist from Message (auto-extract TODO items)"
curl -s -X POST $BASE/checklists/from-message/1 \
  -H "Content-Type: application/json" \
  -d '{}' | jq .

echo ""
echo "13. Get All Checklists"
curl -s $BASE/checklists | jq '.[] | {id, title, item_count: (.items | length)}'

echo ""
echo "14. Add Item to Checklist"
curl -s -X POST $BASE/checklists/$CHECKLIST_ID/items \
  -H "Content-Type: application/json" \
  -d '{"text":"Prepare quarterly report"}' | jq .

echo ""
echo "15. Create Draft Message for Approval"
DRAFT=$(curl -s -X POST $BASE/send/draft \
  -H "Content-Type: application/json" \
  -d '{"platform":"email","to_address":"john.doe@company.com","subject":"Project Status","body":"Hi John,\n\nHere is the latest status on the project."}')
echo $DRAFT | jq .
DRAFT_ID=$(echo $DRAFT | jq .id)

echo ""
echo "16. Get Pending Approvals"
curl -s $BASE/send/pending | jq '.[] | {id, platform, to_address, subject}'

echo ""
echo "17. Reject the Draft (test rejection)"
curl -s -X POST $BASE/send/$DRAFT_ID/reject | jq .

echo ""
echo "18. Setup Email Integration (save encrypted credentials)"
curl -s -X POST "$BASE/integrations/email?master_password=testpass123" \
  -H "Content-Type: application/json" \
  -d '{"credentials":{"smtp_host":"smtp.gmail.com","smtp_port":"587","smtp_user":"your-email@gmail.com","smtp_password":"your-app-password"}}' | jq .

echo ""
echo "19. Get Integrations"
curl -s $BASE/integrations | jq '.[] | {id, platform, status}'

echo ""
echo "=== All Tests Complete ==="
echo ""
echo "To check the database:"
echo "  sqlite3 backend/data/operator.db"
echo "  SELECT * FROM messages;"
echo "  SELECT id, platform, credential_type FROM credentials;"
echo "  .quit"
