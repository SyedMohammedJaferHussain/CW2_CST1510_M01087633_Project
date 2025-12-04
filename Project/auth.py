import bcrypt
USER_DATA_FILE: str = "users.txt"

def HashPassword(plainText: str) -> str:
    """
        Takes planText as paramter, creates salt, hashes, and returns hashed password in UTF-8
    """

    byteStr: bytes = plainText.encode("utf-8")
    salt: bytes = bcrypt.gensalt()
    return bcrypt.hashpw(byteStr, salt).decode("utf-8")


def PasswdVerify(plainText: str, hashPw: str) -> bool:
    """
        Takes password string and hashed password and compares
        Returns True if they match, False if not a match
    """

    textBytes: bytes = plainText.encode("utf-8")
    pWBytes: bytes = hashPw.encode("utf-8")

    if bcrypt.checkpw(textBytes, pWBytes):
        return True
    
    return False


def UserExists(userName: str) -> bool:
    """
        Checks is userName exists in users.txt
    """ 
    try:
        open("users.txt")
    except:
        open("users.txt", "w")
        
    with open("users.txt") as usersFile:
        lines: list[str] = usersFile.readlines()
    
    for line in lines:
        if userName == line.split(",")[0]:
            return True
    
    return False


def ValidateUserName(userName: str) -> tuple:
    """
        Validates username using various crtieria
        Returns: Tuple with bool and string containing error message for wrong username
    """
    criteria: dict[bool, str] = {len(userName) <= 20 and len(userName) >= 3: "Length should be between 3 and 21", userName.isalnum(): "Username can consist of alphanumeric characters only"}
    validated: bool = True
    errorMsg: str = ""
    for condition in criteria:
        if not condition:
            validated = False
            errorMsg += criteria[condition] + "\n"
            
    return (False, errorMsg) if not validated else (True, "")


def ValidatePassWd(passWd: str, confPWrd: str) -> tuple:
    """
        Validates passWd using various crtieria
        Returns: Tuple with bool and string containing error message for wrong password
    """
    criteria: dict[bool, str] = {len(passWd) <= 51 and len(passWd) >= 6 : "Length should be between 6 and 50", "_"  in passWd or "@" in passWd: "Must contain special characters", passWd != confPWrd: "Passwords do not match"}
    validated: bool = True
    errorMsg: str = ""
    for condition in criteria:
        if not condition:
            validated = False
            errorMsg += criteria[condition] + "\n"
            
    return (False, errorMsg) if not validated else (True, "")


def RegisterUser(userName: str, passWd: str) -> bool:
    """
        Get username and password
        Return True, if successful, False if username exists in users.txt
    """
    if UserExists(userName):
        return False

    with open("users.txt", "a") as usersFile:
        usersFile.write(f"\n{userName},{HashPassword(passWd)}")

    return True


def LoginUser(userName: str, passWd: str) -> bool:
    """
        Search through users.txt for username
        Return: True if userName and passWd found, False if userName and passWd not found
    """
    found: bool = False
    hashPwd: str = ""
    with open("users.txt") as usersFile:
        totalText: str = usersFile.read()
        if not totalText:
            return False
        for line in totalText.split("\n"): #Iterating through lines
            if line.split(",")[0] == userName:
                hashPwd = line.split(",")[1]
                found = True
    
    if not found:
        return False
    
    if not PasswdVerify(passWd, hashPwd):
        return False
    
    return True

def DisplayMenu():
    """Displays the main menu options."""
    print("\n" + "="*50)
    print(" MULTI-DOMAIN INTELLIGENCE PLATFORM")
    print(" Secure Authentication System")
    print("="*50)
    print("\n[1] Register a new user")
    print("[2] Login")
    print("[3] Exit")
    print("-"*50)
    
"""    
def Main():
    Main program loop.
    print("\nWelcome to the Week 7 Authentication System!")

    while True:
        DisplayMenu()
        choice = input("\nPlease select an option (1-3): ").strip()
        if choice == '1':
            # Registration flow
            print("\n--- USER REGISTRATION ---")
            userName = input("Enter a username: ").strip()
            # Validate username
            isValid, errorMsg = ValidateUserName(userName)
            
            if not isValid:
                print(f"Error: {errorMsg}")
                continue

            passWord = input("Enter a password: ").strip()
            
            # Validate password
            is_valid, error_msg = ValidatePassWd(passWord)
            if not is_valid:
                print(f"Error: {error_msg}")
                continue

            # Confirm password
            password_confirm = input("Confirm password: ").strip()
            if passWord != password_confirm:
                print("Error: Passwords do not match.")
                continue

            # Register the user
            RegisterUser(userName, passWord)

        elif choice == '2':
            # Login flow
            print("\n--- USER LOGIN ---")
            userName = input("Enter your username: ").strip()
            passWord = input("Enter your password: ").strip()

            # Attempt login
            if LoginUser(userName, passWord):
                print("\nYou are now logged in.")

            # Optional: Ask if they want to logout or exit
            input("\nPress Enter to return to main menu...")

        elif choice == '3':
            # Exit
            print("\nThank you for using the authentication system.")
            print("Exiting...")
            break

        else:
            print("\nError: Invalid option. Please select 1, 2, or 3.")
   
   
if __name__ == "__main__":
    Main()         

test_password = "SecurePassword123"
# Test hashing
hashed = HashPassword(test_password)
print(f"Original password: {test_password}")
print(f"Hashed password: {hashed}")
print(f"Hash length: {len(hashed)} characters")

is_valid = PasswdVerify(test_password, hashed)
print(f"\nVerification with correct password: {is_valid}")

is_invalid = PasswdVerify("WrongPassword", hashed)
print(f"Verification with incorrect password: {is_invalid}")
"""