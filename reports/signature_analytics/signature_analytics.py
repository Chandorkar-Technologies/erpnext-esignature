import frappe
from frappe.utils import getdate, add_days
from datetime import datetime, timedelta

def execute(filters=None):
    """Signature Analytics Report"""
    columns = get_columns()
    data = get_data(filters)
    chart = get_chart_data(data)
    
    return columns, data, None, chart

def get_columns():
    return [
        {
            "fieldname": "period",
            "label": "Period",
            "fieldtype": "Data",
            "width": 100
        },
        {
            "fieldname": "total_requests",
            "label": "Total Requests",
            "fieldtype": "Int",
            "width": 120
        },
        {
            "fieldname": "signed_requests",
            "label": "Signed",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "pending_requests",
            "label": "Pending",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "expired_requests",
            "label": "Expired",
            "fieldtype": "Int",
            "width": 100
        },
        {
            "fieldname": "success_rate",
            "label": "Success Rate %",
            "fieldtype": "Percent",
            "width": 120
        },
        {
            "fieldname": "avg_signing_time",
            "label": "Avg Signing Time (Hours)",
            "fieldtype": "Float",
            "width": 150
        }
    ]

def get_data(filters):
    """Generate analytics data"""
    if not filters:
        filters = {}
    
    # Set default date range
    if not filters.get("from_date"):
        filters["from_date"] = add_days(datetime.now().date(), -30)
    if not filters.get("to_date"):
        filters["to_date"] = datetime.now().date()
    
    # Get signature requests data
    signature_requests = frappe.db.sql("""
        SELECT 
            DATE(creation) as date,
            status,
            TIMESTAMPDIFF(HOUR, creation, signed_at) as signing_time_hours
        FROM `tabSignature Request`
        WHERE DATE(creation) BETWEEN %s AND %s
        ORDER BY creation
    """, (filters["from_date"], filters["to_date"]), as_dict=True)
    
    # Group by date and calculate metrics
    date_wise_data = {}
    for req in signature_requests:
        date_str = req.date.strftime("%Y-%m-%d")
        if date_str not in date_wise_data:
            date_wise_data[date_str] = {
                "period": date_str,
                "total_requests": 0,
                "signed_requests": 0,
                "pending_requests": 0,
                "expired_requests": 0,
                "signing_times": []
            }
        
        date_wise_data[date_str]["total_requests"] += 1
        
        if req.status == "Signed":
            date_wise_data[date_str]["signed_requests"] += 1
            if req.signing_time_hours:
                date_wise_data[date_str]["signing_times"].append(req.signing_time_hours)
        elif req.status in ["Sent", "Viewed"]:
            date_wise_data[date_str]["pending_requests"] += 1
        elif req.status == "Expired":
            date_wise_data[date_str]["expired_requests"] += 1
    
    # Calculate derived metrics
    data = []
    for date_data in date_wise_data.values():
        total = date_data["total_requests"]
        signed = date_data["signed_requests"]
        
        date_data["success_rate"] = (signed / total * 100) if total > 0 else 0
        
        signing_times = date_data["signing_times"]
        date_data["avg_signing_time"] = sum(signing_times) / len(signing_times) if signing_times else 0
        
        # Remove helper field
        del date_data["signing_times"]
        
        data.append(date_data)
    
    return sorted(data, key=lambda x: x["period"])

def get_chart_data(data):
    """Generate chart data"""
    return {
        "data": {
            "labels": [d["period"] for d in data],
            "datasets": [
                {
                    "name": "Total Requests",
                    "values": [d["total_requests"] for d in data]
                },
                {
                    "name": "Signed",
                    "values": [d["signed_requests"] for d in data]
                },
                {
                    "name": "Success Rate %",
                    "values": [d["success_rate"] for d in data]
                }
            ]
        },
        "type": "line"
    }
