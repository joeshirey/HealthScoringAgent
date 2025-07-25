import re

def remove_comments(code: str, language: str) -> str:
    """
    Removes comments from a code string based on the language.
    """
    if language.lower() in ["python", "shell", "ruby"]:
        # Removes single-line comments starting with #
        return re.sub(r"#.*", "", code)
    elif language.lower() in ["javascript", "java", "c", "c++", "c#", "go", "swift", "typescript", "kotlin", "rust", "php", "terraform"]:
        # Removes single-line // comments and multi-line /* ... */ comments
        code = re.sub(r"//.*", "", code)
        code = re.sub(r"/\*.*?\*/", "", code, flags=re.DOTALL)
        return code
    elif language.lower() in ["html", "xml"]:
        # Removes <!-- ... --> comments
        return re.sub(r"<!--.*?-->", "", code, flags=re.DOTALL)
    else:
        # Return original code if language is not supported
        return code
