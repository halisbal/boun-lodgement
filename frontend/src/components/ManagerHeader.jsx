import useAuth from "../hooks/useAuth"

const ManagerHeader = ({children}) => {
    const {isLoggedIn, user} = useAuth();
    console.log("mh : ", user)
    console.log("mh : ", isLoggedIn)

    if(!isLoggedIn){
        return <div></div>  
    }
    if(user?.role !== 'Manager'){
        console.log("mh : ", user?.role)
        return <div></div>
    }

    return (
        <div>
            {children}
        </div>
    )
}

export default ManagerHeader