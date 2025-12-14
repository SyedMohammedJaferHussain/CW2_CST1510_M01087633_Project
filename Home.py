import streamlit as st
import app.data.schema as Schema
import app.data.tickets as tickets
import app.data.incidents as incidents
import app.data.datasets as datasets
import app.data.users as Users
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
            When button pressed, goes to users.py and checks if login is successful.
            If yes, goes to Cyber_Analytics
            
        Args:
            loginTab (_DeltaGenerator_): Tab in which login widgets go in
    """
    with loginTab:
        st.subheader("Login")

        loginUsername = st.text_input("Username", key="login_username")
        loginPasswd = st.text_input("Password", type="password", key="login_password")

        if st.button("Log in", type = "primary"):
            # Simple credential check (for teaching only – not secure!)
            loginSuccess: bool = Users.LoginUser(loginUsername, loginPasswd)
            if loginSuccess:
                st.session_state.logged_in = True
                st.session_state.username = loginUsername
                st.success(f"Welcome back, {loginUsername}! ")

                # Redirect to dashboard page
                st.switch_page("pages/1_IT_Tickets.py")
            else:
                st.error("Username or password is incorrect")


def Register(registerTab): 
    """
        Explanation:
            Gets user input through widgets for username, password, and confirm password
            When button press, goes to users.py and validates username and password.
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
            
            registerRes = Users.RegisterUser(new_username, new_password, confirm_password)
            if registerRes:
                st.error(registerRes)                
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
    with open("DATA/users.bin", "wb") as usersObjs:
        pickle.dump(usersLst, usersObjs)


if __name__ == "__main__": 
    ticketsLst = tickets.TransferFromDB()
    incidentsLst = incidents.TransferFromDB()
    datasetsLst = datasets.TransferFromDB()
    usersLst = Users.TransferFromDB()
    SerializeObjs()
    Schema.CreateAllTables()
    LoginCheck()
    GoCyber()
    logTab, regTab = ConfigLayout()
    Register(regTab)
    Login(logTab)