import constants

START, TITLE, CAST, BODY, FUNCTION_START, FUNCTION_TITLE, FUNCTION_CAST, FUNCTION_BODY, END = range(9)

transitions = []
transitions.insert(START, (TITLE, CAST, BODY, FUNCTION_START))
transitions.insert(TITLE, (CAST, BODY, FUNCTION_TITLE))
transitions.insert(CAST, (BODY, FUNCTION_CAST))
transitions.insert(BODY, (FUNCTION_BODY, END))
transitions.insert(FUNCTION_START, (START))
transitions.insert(FUNCTION_TITLE, (TITLE))
transitions.insert(FUNCTION_CAST, (CAST))
transitions.insert(FUNCTION_BODY, (BODY, END))
