final_prompt = f"""You are strict classifiction model.

    Your Task:
        Decide whether the user's latest messages is aksing to continue, explain, refine or modify the same previously generated SQL query or specifying more 
        to resolve ambigity on previous user query, or whether it is a new request.

    1.SAME_SQL_CONTINUE_OR_MODIFY:
        The user is referring to previously genearted sql query and wants to continue, explain, run, format, optimise, or modify it.

    2.NEW_SQL_REQUEST:
        The user is asking for a new SQL query or new data extraction/analysis request taht is not clearly a continuation of previousl sql.

    CURRENT USER REQUEST: {last_user_query}
    LAST USER QUERY: {previous_user_query}
    LAST AGENT STATE:
        SESSION_SUMMARY: {state.get('user_session_summary', None)}
        PREVIOUS_INTENT: {state.get('intent', None)}
        LAST_VALIDATED_SQL: {state.get('last_validated_sql', None)}

    """