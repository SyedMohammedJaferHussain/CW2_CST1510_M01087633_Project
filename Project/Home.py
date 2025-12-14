import streamlit as st
import app.services.user_service as LoginRegister
import app.data.schema as Schema
import auth
import app.data.ticketsClass as tickets
import app.data.incidentsClass as incidents
import app.data.datasets as datasets
import pickle


def LoginCheck() -> None:
    """
        Checks if user has logged in through Login Page. Sets values to False/None if not
    """
    if "users" not in st.session_state:
        
        st.session_state.users = {}

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if "username" not in st.session_state:
        st.session_state.username = ""


def ConfigLayout():
    """
        Configures page layout and creates tabs for login and register
        Returns: tab_login, tab_register: DeltaGenerator (Tabs)
    """
    st.set_page_config(page_title="Login / Register", page_icon="🔑", layout="centered")
    st.title("Welcome")
    tab_login, tab_register = st.tabs(["Login", "Register"])
    return tab_login, tab_register


def GoCyber() -> None:
    """
        Checks if user's logged in, if yes switches page to Cyber_Analytics.py
        Returns: None
    """
    if st.session_state.logged_in:
        st.success(f"Already logged in as **{st.session_state.username}**.")
        if st.button("Go To IT Tickets"):
            st.switch_page("pages/1_IT_Tickets.py")
        st.stop()  # Don’t show login/register again


def Login(loginTab) -> None:
    """
        Explanation: 
            Creates textboxes for user input for username and password. 
            When button pressed, goes to user_service.py and checks if login is successful.
            If yes, goes to Cyber_Analytics
            
        Args:
            loginTab (_DeltaGenerator_): Tab in which login widgets go in
    """
    with loginTab:
        st.subheader("Login")

        loginUsername = st.text_input("Username", key="login_username")
        loginPasswd = st.text_input("Password", type="password", key="login_password")

        if st.button("Log in", type="primary"):
            # Simple credential check (for teaching only – not secure!)
            loginSuccess: tuple = LoginRegister.LoginUser(loginUsername, loginPasswd)
            if loginSuccess[0]:
                st.session_state.logged_in = True
                st.session_state.username = loginUsername
                st.success(f"Welcome back, {loginUsername}! ")

                # Redirect to dashboard page
                st.switch_page("pages/1_IT_Tickets.py")
            else:
                st.error(loginSuccess[1])


def Register(registerTab): 
    """
        Explanation:
            Gets user input through widgets for username, password, and confirm password
            When button press, goes to auth.py and validates username and password.
            If validated, registers through user_service.py
            If not validated, displays appropriate warning/error
        Args:
            registerTab (_DeltaGenerator_): _description_
    """
    with registerTab:
        st.subheader("Register")

        new_username = st.text_input("Choose a username", key="register_username")
        new_password = st.text_input("Choose a password", type="password", key="register_password")
        confirm_password = st.text_input("Confirm password", type="password", key="register_confirm")

        if st.button("Create account"):
            # Basic checks – again, just for teaching
            if not new_username or not new_password:
                st.warning("Please fill in all fields.")
            
            checkValidName: tuple = auth.ValidateUserName(new_username)
            checkValidPWrd: tuple = auth.ValidatePassWd(new_password, confirm_password)
            if checkValidName[0] == False:
                st.error(checkValidName[1])
            if checkValidPWrd[0] == False:
                st.write(new_password == confirm_password)
            
            checkRegister: tuple = LoginRegister.RegisterUser(new_username, new_password)
            if not checkRegister[0]: #Failure
                st.error(checkRegister[1])
                
            else:
                st.session_state.users[new_username] = new_password
                st.success("Account created! You can now log in from the Login tab.")
                st.info("Tip: go to the Login tab and sign in with your new account.")


def SerializeObjs():
    """
        Uses pickle module to serialize(pickle) tickets (+ other classes) into binary files for reading from other files
    """
    with open("DATA/tickets.bin", "wb") as ticketsObjs:
        pickle.dump(ticketsLst, ticketsObjs)
    with open("DATA/incidents.bin", "wb") as incidentsObjs:
        pickle.dump(incidentsLst, incidentsObjs)
    with open("DATA/datasets.bin", "wb") as datasetsObjs:
        pickle.dump(datasetsLst, datasetsObjs)


if __name__ == "__main__": 
    ticketsLst = tickets.TransferFromDB()
    incidentsLst = incidents.TransferFromDB()
    datasetsLst = datasets.TransferFromDB()
    SerializeObjs()
    Schema.CreateAllTables()
    LoginCheck()
    GoCyber()
    logTab, regTab = ConfigLayout()
    Register(regTab)
    Login(logTab)