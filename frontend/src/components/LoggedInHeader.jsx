import useAuth from "../hooks/useAuth"

const LoggedInHeader = ({children}) => {
    const {isLoggedIn} = useAuth();

    if(!isLoggedIn){
        return <div></div>  
    }

    return (
        <div>
            {children}
        </div>
    )
}

export default LoggedInHeader