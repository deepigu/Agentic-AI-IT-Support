
def diagnose_issue(issue: str):

    # Convert the user's message to lowercase
    issue = issue.lower()

    # Network problems
    if any(word in issue for word in [
        "wifi", "wi-fi", "internet", "network", "dns"
    ]):
        return {
            "category": "Network Issue",
            "suggestion": "Check your network connection, restart your router, and verify DNS settings."
        }

    # Login and authentication problems
    elif any(word in issue for word in [
        "password", "login", "sign in", "locked account"
    ]):
        return {
            "category": "Authentication Issue",
            "suggestion": "Verify your credentials and use the approved password reset process."
        }

    # Computer performance problems
    elif any(word in issue for word in [
        "slow", "freezing", "lagging", "performance"
    ]):
        return {
            "category": "Performance Issue",
            "suggestion": "Check CPU and memory usage, close unnecessary applications, and restart the computer."
        }

    # Printer problems
    elif any(word in issue for word in [
        "printer", "printing", "print job"
    ]):
        return {
            "category": "Printer Issue",
            "suggestion": "Check printer connectivity, paper supply, and print queue."
        }

    # Email problems
    elif any(word in issue for word in [
        "email", "outlook", "mailbox"
    ]):
        return {
            "category": "Email Issue",
            "suggestion": "Check internet connectivity, email service status, and account configuration."
        }

    # Unknown problems
    else:
        return {
            "category": "General IT Issue",
            "suggestion": "Collect additional information and escalate to IT support if necessary."
        }
