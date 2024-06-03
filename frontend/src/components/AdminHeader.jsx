import useAuth from "../hooks/useAuth"

const AdminHeader = ({children}) => {
    const {isLoggedIn, user} = useAuth();
    console.log("mh : ", user)
    console.log("mh : ", isLoggedIn)

    if(!isLoggedIn){
        return <div></div>  
    }
    if(user?.role !== 'Admin'){
        return <div></div>
    }

    return (
        <div>
            {children}
        </div>
    )
}

export default AdminHeader;