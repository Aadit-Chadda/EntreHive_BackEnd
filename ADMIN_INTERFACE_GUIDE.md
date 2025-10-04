# Contact Admin Interface - Visual Guide

## Quick Reference for Managing Contact Inquiries

---

## 🎨 Admin Dashboard Layout

### List View Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Contact Management > Contact Inquiries                                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│ 📊 Summary Stats:                                                        │
│   New: 5 | In Progress: 3 | Resolved: 12                                │
│                                                                           │
│ 🔍 Search: [________________________] 🔎                                 │
│                                                                           │
│ 📅 Date Hierarchy: 2025 > October > 4                                   │
│                                                                           │
│ 🎯 Filters:                                                              │
│   ☐ Status: All / New / In Progress / Resolved / Closed                 │
│   ☐ Priority: All / Low / Medium / High / Urgent                         │
│   ☐ Type: All / General / Partnership / University...                    │
│   ☐ Date: Today / Past 7 days / This month...                           │
│                                                                           │
│ 📋 Actions: [Mark as New ▼] [Go]                                        │
│                                                                           │
├─────────────────────────────────────────────────────────────────────────┤
│ ID | Name          | Email           | Type      | Subject | Priority  |│
│────|─────────────--|-----------------|-----------|---------|-----------|│
│ ☐5 | 🆕 Jane Smith | jane@...        | 🔵 PARTNER| Need... | 🟠 HIGH   |│
│ ☐4 | John Doe      | john@...        | 🔴 TECH   | Bug...  | 🔥 URGENT |│
│ ☐3 | Mike Ross     | mike@...        | 🟢 UNIV   | Collab..| ➡️ MEDIUM |│
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 Color Scheme Reference

### Status Badges

| Status | Color | Badge |
|--------|-------|-------|
| New | Blue (#007bff) | 🔵 **NEW** |
| In Progress | Yellow (#ffc107) | 🟡 **IN PROGRESS** |
| Resolved | Green (#28a745) | 🟢 **RESOLVED** |
| Closed | Gray (#6c757d) | ⚫ **CLOSED** |

### Priority Badges

| Priority | Color | Badge |
|----------|-------|-------|
| Low | Green | 🟢 ⬇️ **Low** |
| Medium | Yellow | 🟡 ➡️ **Medium** |
| High | Orange | 🟠 ⬆️ **High** |
| Urgent | Red | 🔴 🔥 **Urgent** |

### Inquiry Type Badges

| Type | Color | Badge |
|------|-------|-------|
| General | Gray | **General Inquiry** |
| Partnership | Blue | **Partnership Opportunity** |
| University | Green | **University Partnership** |
| Technical | Red | **Technical Support** |
| Feedback | Cyan | **Feedback & Suggestions** |
| Investor | Yellow | **Investor Relations** |
| Press | Purple | **Press & Media** |
| Other | Gray | **Other** |

---

## 📋 Available Filters

### 1. Status Filter
```
☐ All
☐ New (5)
☐ In Progress (3)
☐ Resolved (12)
☐ Closed (8)
```

### 2. Priority Filter
```
☐ All
☐ Low (10)
☐ Medium (8)
☐ High (7)
☐ Urgent (3)
```

### 3. Inquiry Type Filter
```
☐ All
☐ General Inquiry (12)
☐ Partnership Opportunity (5)
☐ University Partnership (4)
☐ Technical Support (3)
☐ Feedback & Suggestions (2)
☐ Investor Relations (1)
☐ Press & Media (1)
☐ Other (0)
```

### 4. Date Filters
```
☐ Today
☐ Past 7 days
☐ This month
☐ This year
☐ Custom range...
```

### 5. Assigned To Filter
```
☐ Unassigned
☐ [Staff Member 1]
☐ [Staff Member 2]
```

---

## ⚡ Bulk Actions

Select multiple inquiries using checkboxes, then choose an action:

### Status Actions
- ✅ **Mark as New** - Reset to new status
- 🔄 **Mark as In Progress** - Set as being worked on
- ✓ **Mark as Resolved** - Complete with timestamp
- 🔒 **Mark as Closed** - Archive the inquiry

### Priority Actions
- 🔴 **Set Priority: High** - Mark as high priority
- 🟡 **Set Priority: Medium** - Set to medium
- 🟢 **Set Priority: Low** - Reduce priority

---

## 📝 Detail View Layout

When clicking on an inquiry, you'll see:

```
┌─────────────────────────────────────────────────────────────┐
│ Contact Inquiry #123                                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│ ═══════════════════════════════════════════════════════════ │
│ CONTACT INFORMATION                                          │
│ ═══════════════════════════════════════════════════════════ │
│                                                               │
│ ID:           #123                                           │
│ Name:         John Doe                                       │
│ Email:        john@example.com ✉️ (clickable)                │
│ Submitted:    2025-10-04 14:30:25                           │
│                                                               │
│ ═══════════════════════════════════════════════════════════ │
│ INQUIRY DETAILS                                              │
│ ═══════════════════════════════════════════════════════════ │
│                                                               │
│ Type:         🔴 Technical Support                           │
│ Subject:      Website login issue                            │
│                                                               │
│ Message:                                                     │
│ ┌───────────────────────────────────────────────────────┐  │
│ │ I am unable to log in to my account. I keep getting  │  │
│ │ an error message saying "Invalid credentials" even    │  │
│ │ though I am sure my password is correct. Can you     │  │
│ │ please help?                                          │  │
│ └───────────────────────────────────────────────────────┘  │
│                                                               │
│ ═══════════════════════════════════════════════════════════ │
│ MANAGEMENT                                                   │
│ ═══════════════════════════════════════════════════════════ │
│                                                               │
│ Status:       [New ▼]                                        │
│ Priority:     [High ▼]                                       │
│ Assigned To:  [Select staff... ▼]                           │
│                                                               │
│ Admin Notes:  ┌─────────────────────────────────────────┐  │
│               │ Contacted user via email                 │  │
│               │ Sent password reset link                 │  │
│               │ Following up in 24h                      │  │
│               └─────────────────────────────────────────┘  │
│                                                               │
│ ▼ TECHNICAL INFORMATION (Click to expand)                   │
│                                                               │
│ ▼ TIMESTAMPS (Click to expand)                              │
│                                                               │
│ [Save and continue editing] [Save and add another] [Save]   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔍 Search Functionality

### Searchable Fields:
- ✅ Name
- ✅ Email address
- ✅ Subject line
- ✅ Message content
- ✅ Admin notes
- ✅ Inquiry ID

### Search Examples:
```
john@example.com     → Find by email
Technical Support    → Find by inquiry type
#123                → Find by ID
password reset      → Search in messages
```

---

## 📊 Response Time Indicators

### Active Inquiries (Not Resolved):
- **Less than 24h:** `Pending 5h` (orange)
- **1-2 days:** `Pending 1d 12h` (orange)
- **Over 2 days:** `Pending 3d 8h` (red, attention needed)

### Resolved Inquiries:
- **Response time:** `1d 4h` (normal text)
- **Fast response:** `6h` (green, under 24h)

---

## 🎯 Workflow Examples

### Example 1: New Technical Support Inquiry

1. **Inquiry arrives** → Shows with 🆕 indicator and 🔴 **TECH** badge
2. **Auto-priority** → Set to 🟠 High automatically
3. **Admin action:**
   - Opens inquiry
   - Reviews technical details
   - Assigns to Tech Support staff
   - Changes status to 🟡 In Progress
   - Adds note: "Investigating login issue"
4. **Resolution:**
   - Fixes issue
   - Marks as 🟢 Resolved
   - System auto-timestamps resolution

### Example 2: Partnership Inquiry

1. **Inquiry type:** Partnership Opportunity (🔵 Blue badge)
2. **Auto-priority:** ➡️ Medium
3. **Admin workflow:**
   - Filter by "Partnership" type
   - Bulk select relevant inquiries
   - Assign all to Business Development team
   - Mark as In Progress
   - Add follow-up dates in notes

### Example 3: Bulk Management

1. **Select inquiries:**
   - Use checkboxes to select 5 inquiries
2. **Choose action:**
   - "Mark as In Progress" from dropdown
3. **Click "Go"**
4. **Confirmation:** "5 inquiries marked as In Progress"

---

## 🎨 Special Indicators

### New Inquiry Indicator
```
🆕 Jane Smith    →    Unread/new inquiry (bold name)
John Doe         →    Already viewed
```

### Response Time Alerts
```
Pending 8h       →    Normal (black text)
Pending 36h      →    Warning (orange text)
Pending 4d       →    Critical (red text)
```

### Priority Icons
```
⬇️  Low priority
➡️  Medium priority
⬆️  High priority
🔥 Urgent priority
```

---

## 💡 Pro Tips

### 1. Quick Filtering
- Click on any badge (status/priority/type) to filter by that value
- Use date hierarchy at top for quick date filtering
- Combine filters for precise results

### 2. Efficient Management
- Use bulk actions for similar inquiries
- Set up custom filters (Django allows saving filter sets)
- Sort by "Created At" to see newest first

### 3. Search Tips
- Use quotes for exact phrases: `"password reset"`
- Search by ID with #: `#123`
- Email searches work on partial matches

### 4. Assignment Strategy
- Filter by inquiry type, then bulk assign to relevant team
- Use "Unassigned" filter to catch new items
- Track workload by filtering by assigned staff

### 5. Status Management
- Keep "New" for truly unviewed items
- Move to "In Progress" when actively working
- "Resolved" when user issue is fixed
- "Closed" for archived/complete inquiries

---

## 📞 Common Admin Tasks

### Daily Tasks:
1. ✅ Check for new inquiries (filter by Status: New)
2. ✅ Respond to high/urgent priorities first
3. ✅ Update status on active inquiries
4. ✅ Add notes for team communication

### Weekly Tasks:
1. ✅ Review response times
2. ✅ Archive resolved inquiries (mark as Closed)
3. ✅ Analyze inquiry type trends
4. ✅ Reassign stale inquiries

### Monthly Tasks:
1. ✅ Generate reports (export data)
2. ✅ Review average response times
3. ✅ Clean up old closed inquiries
4. ✅ Update priority assignments if needed

---

## 🎓 Training Checklist

For new admins, ensure they can:

- [ ] Access the admin dashboard
- [ ] Navigate to Contact Inquiries section
- [ ] Understand color coding (status/priority/type)
- [ ] Filter inquiries by various criteria
- [ ] Search for specific inquiries
- [ ] Open and review inquiry details
- [ ] Update status and priority
- [ ] Add admin notes
- [ ] Assign inquiries to staff
- [ ] Use bulk actions
- [ ] Understand response time indicators
- [ ] Mark inquiries as resolved/closed

---

## 📚 Quick Reference Card

```
╔═══════════════════════════════════════════════════╗
║         CONTACT ADMIN QUICK REFERENCE             ║
╠═══════════════════════════════════════════════════╣
║ Access: /admin/contact/contactinquiry/           ║
║                                                   ║
║ STATUS COLORS:                                    ║
║ 🔵 New | 🟡 In Progress | 🟢 Resolved | ⚫ Closed║
║                                                   ║
║ PRIORITY:                                         ║
║ ⬇️ Low | ➡️ Medium | ⬆️ High | 🔥 Urgent         ║
║                                                   ║
║ QUICK ACTIONS:                                    ║
║ • Click badge to filter                          ║
║ • Use checkboxes for bulk actions                ║
║ • Search by name/email/content                   ║
║ • Sort by clicking column headers                ║
║                                                   ║
║ TARGET RESPONSE TIME: 24-48 hours                ║
╚═══════════════════════════════════════════════════╝
```

---

**Admin Interface Version:** 1.0.0  
**Last Updated:** October 4, 2025  
**Status:** Production Ready ✅

