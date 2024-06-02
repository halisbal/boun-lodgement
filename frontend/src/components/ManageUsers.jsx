import {
    MagnifyingGlassIcon,
    ChevronUpDownIcon,
} from "@heroicons/react/24/outline";
import { PencilIcon, UserPlusIcon } from "@heroicons/react/24/solid";
import {
    Card,
    CardHeader,
    Input,
    Typography,
    Button,
    CardBody,
    Chip,
    CardFooter,
    Tabs,
    TabsHeader,
    Tab,
    IconButton,
    Tooltip,
    Dialog,
    DialogHeader,
    DialogBody,
    DialogFooter,
    Select,
    Option,
    Checkbox,

} from "@material-tailwind/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { apiService } from "../services/apiService";
import { defer } from "react-router-dom";
import MyAlert from "./MyAlert";


const ROLES = {
    "1": "User",
    "2": "Manager",
    "3": "Admin"
}
const ROLES_REVERSE = {
    "User": "1",
    "Manager": "2",
    "Admin": "3"
}

const TYPES = {
    "1": "Akademik",
    "2": "İdari",
    "3": "Görevli"
}
const TYPES_REVERSE = {
    "Akademik": "1",
    "İdari": "2",
    "Görevli": "3"
}


const TABS = [
    {
        label: "All",
        value: "all",
    },
    {
        label: "Akademik",
        value: "Akademik",
    },
    {
        label: "İdari",
        value: "İdari",
    },
    {
        label: "Görevli",
        value: "Görevli",
    },
];

const TABLE_HEAD = ["ID", "Name", "Email", "Role", "Type", "Is Active", "Join Date", ""];

const ManageUsers = () => {
    const { data: users, isLoading, error } = useQuery(["all-users"], () => apiService.get(`/auth/user/`));
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(6);
    const [activeTab, setActiveTab] = useState("all");
    const [sortConfig, setSortConfig] = useState({ key: "id", direction: "ascending" });
    const [searchQuery, setSearchQuery] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState({});
    const [alert, setAlert] = useState({ message: '', type: 'success', visible: false });

    const queryClient = useQueryClient();

    const filteredUsers = useMemo(() => {
        let filtered = users || [];

        if (activeTab !== "all") {
            console.log("activeTab : ", activeTab)

            filtered = filtered.filter(user => user.type === activeTab);
        }

        if (searchQuery) {
            filtered = filtered.filter(user =>
                user.first_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                user.last_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                user.email.toLowerCase().includes(searchQuery.toLowerCase())
            );
        }

        return filtered;
    }, [users, activeTab, searchQuery]);

    const sortedUsers = useMemo(() => {
        const sortableItems = [...filteredUsers];
        sortableItems.sort((a, b) => {
            if (a[sortConfig.key] < b[sortConfig.key]) {
                return sortConfig.direction === "ascending" ? -1 : 1;
            }
            if (a[sortConfig.key] > b[sortConfig.key]) {
                return sortConfig.direction === "ascending" ? 1 : -1;
            }
            return 0;
        });
        return sortableItems;
    }, [filteredUsers, sortConfig]);

    const paginatedUsers = useMemo(() => {
        const startIndex = (currentPage - 1) * itemsPerPage;
        return sortedUsers.slice(startIndex, startIndex + itemsPerPage);
    }, [sortedUsers, currentPage, itemsPerPage]);

    const handleSort = key => {
        let direction = "ascending";
        if (sortConfig.key === key && sortConfig.direction === "ascending") {
            direction = "descending";
        }
        setSortConfig({ key, direction });
    };

    const handleEditSelection = (id) => {
        const user = users.find(user => user.id === id);
        console.log("user : ", user);
        const editedUser = { ...user, role: ROLES_REVERSE[user.role], type: TYPES_REVERSE[user.type] };
        console.log("editedUser : ", editedUser);
        setSelectedUser(editedUser);
        setIsOpen(true);
    }

    const handleSave = () => {

        console.log("selectedUser : ", selectedUser);
        apiService.patch(`/auth/user/${selectedUser.id}/edit/`, selectedUser).then((res) => {
            console.log("Response : ", res);
            if (res) {
                queryClient.invalidateQueries("all-users");
                console.log("User updated successfully");
                showAlert("User updated successfully");

                setIsOpen(false);
            } else {
                console.log("Error updating user");
                showAlert("Error updating user", "error");
                setIsOpen(false);
            }
        }
        ).catch((err) => {
            console.log("Error : ", err);
            showAlert("Error updating user", "error");
            setIsOpen(false);
        }).finally(() => {
            setSelectedUser({});
        });


    }


    const showAlert = (message, type = 'success') => {
        setAlert({ message, type, visible: true });

        // Automatically close the alert after 3 seconds
        setTimeout(() => {
            setAlert({ ...alert, visible: false });
        }, 3000);
    };

    const closeAlert = () => {
        setAlert({ ...alert, visible: false });
    };




    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="flex justify-center">
            {alert.visible && <MyAlert message={alert.message} type={alert.type} onClose={closeAlert} visible={alert.visible} />}
            <Card className="h-full w-11/12 mt-8">
                <CardHeader floated={false} shadow={false} className="rounded-none">
                    <div className="mb-8 flex items-center justify-between gap-8">
                        <div>
                            <Typography variant="h5" color="blue-gray">
                                Users list
                            </Typography>
                        </div>
                        <div className="flex shrink-0 flex-col gap-2 sm:flex-row">

                        </div>
                    </div>
                    <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
                        <Tabs value={activeTab} className="w-full md:w-max" >
                            <TabsHeader>
                                {TABS.map(({ label, value }) => (
                                    <Tab key={value} value={value} onClick={() => setActiveTab(value)}>
                                        &nbsp;&nbsp;{label}&nbsp;&nbsp;
                                    </Tab>
                                ))}
                            </TabsHeader>
                        </Tabs>
                        <div className="w-full md:w-72">
                            <Input
                                label="Search"
                                icon={<MagnifyingGlassIcon className="h-5 w-5" />}
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                            />
                        </div>
                    </div>
                </CardHeader>
                <CardBody className="overflow-scroll px-0">
                    <table className="mt-4 w-full min-w-max table-auto text-left">
                        <thead>
                            <tr>
                                {TABLE_HEAD.map((head, index) => (
                                    <th
                                        key={head}
                                        className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50"
                                        onClick={() => handleSort(head.toLowerCase().replace(" ", "_"))}
                                    >
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="flex items-center justify-between gap-2 font-normal leading-none opacity-70"
                                        >
                                            {head}
                                            {index !== TABLE_HEAD.length - 1 && (
                                                <ChevronUpDownIcon strokeWidth={2} className="h-4 w-4" />
                                            )}
                                        </Typography>
                                    </th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {paginatedUsers.map(
                                ({ id, first_name, last_name, email, role, type, is_active, date_joined }, index) => {
                                    const isLast = index === paginatedUsers.length - 1;
                                    const classes = isLast
                                        ? "p-4"
                                        : "p-4 border-b border-blue-gray-50";

                                    return (
                                        <tr key={id}>
                                            <td className={classes}>
                                                <Typography
                                                    variant="small"
                                                    color="blue-gray"
                                                    className="font-normal"
                                                >
                                                    {id}
                                                </Typography>
                                            </td>
                                            <td className={classes}>
                                                <div className="flex items-center gap-3">
                                                    <Typography
                                                        variant="small"
                                                        color="blue-gray"
                                                        className="font-normal"
                                                    >
                                                        {first_name + " " + last_name}
                                                    </Typography>
                                                </div>
                                            </td>
                                            <td className={classes}>
                                                <Typography
                                                    variant="small"
                                                    color="blue-gray"
                                                    className="font-normal"
                                                >
                                                    {email}
                                                </Typography>
                                            </td>
                                            <td className={classes}>
                                                <Typography
                                                    variant="small"
                                                    color="blue-gray"
                                                    className="font-normal"
                                                >
                                                    {role}
                                                </Typography>
                                            </td>
                                            <td className={classes}>
                                                <Typography
                                                    variant="small"
                                                    color="blue-gray"
                                                    className="font-normal"
                                                >
                                                    {type}
                                                </Typography>
                                            </td>
                                            <td className={classes}>
                                                <div className="w-max">
                                                    <Chip
                                                        variant="ghost"
                                                        size="sm"
                                                        value={is_active ? "Active" : "Inactive"}
                                                        color={is_active ? "green" : "blue-gray"}
                                                    />
                                                </div>
                                            </td>
                                            <td className={classes}>
                                                <Typography
                                                    variant="small"
                                                    color="blue-gray"
                                                    className="font-normal"
                                                >
                                                    {new Date(date_joined).toLocaleString(undefined, {
                                                        year: "numeric",
                                                        month: "long",
                                                        day: "2-digit",
                                                        hour: "2-digit",
                                                        minute: "2-digit",
                                                    })}
                                                </Typography>
                                            </td>
                                            <td className={classes}>
                                                <Tooltip content="Edit User">
                                                    <IconButton variant="text" onClick={() => handleEditSelection(id)}>
                                                        <PencilIcon className="h-4 w-4" />
                                                    </IconButton>
                                                </Tooltip>
                                            </td>
                                        </tr>
                                    );
                                }
                            )}
                        </tbody>
                    </table>
                </CardBody>
                <CardFooter className="flex items-center justify-between border-t border-blue-gray-50 p-4">
                    <Typography variant="small" color="blue-gray" className="font-normal">
                        Page {currentPage} of {Math.ceil(filteredUsers.length / itemsPerPage)}
                    </Typography>
                    <div className="flex gap-2">
                        <Button variant="outlined" size="sm" onClick={() => setCurrentPage(page => Math.max(page - 1, 1))}>
                            Previous
                        </Button>
                        <Button variant="outlined" size="sm" onClick={() => setCurrentPage(page => Math.min(page + 1, Math.ceil(filteredUsers.length / itemsPerPage)))}>
                            Next
                        </Button>
                    </div>
                </CardFooter>
            </Card>

            <Dialog size='xs' open={isOpen} handler={setIsOpen}>
                <DialogHeader>User Info</DialogHeader>
                <DialogBody className="px-8" >
                    <Typography color='blue-gray' className='mb-3 font-normal' variant='h6'>ID : {selectedUser.id}</Typography>
                    <Typography color='blue-gray' className='mb-3 font-normal' variant='h6'>Name : {selectedUser.first_name + " " + selectedUser.last_name}</Typography>
                    <Typography color='blue-gray' className='mb-4 font-normal' variant='h6'>Email : {selectedUser.email}</Typography>
                    <div className="flex flex-row mb-3 items-center ">
                        <div className="w-2/12" >
                            <Typography color='blue-gray' className='font-normal' variant='h6'>Role :  </Typography>
                        </div>
                        <div className="w-9/12">
                            <Select variant="static" value={selectedUser.role} onChange={(val) => setSelectedUser(
                                (prevState) => ({
                                    ...prevState,
                                    role: val
                                })
                            )}>
                                {Object.keys(ROLES).map((role) => (
                                    <Option key={role} value={role}>
                                        {ROLES[role]}
                                    </Option>
                                ))}
                            </Select>
                        </div>
                    </div>

                    <div className="flex flex-row items-center mb-3 ">
                        <div className="w-2/12">
                            <Typography color='blue-gray' className="font-normal" variant='h6'>Type :  </Typography>
                        </div>
                        <div className="w-9/12">
                            <Select variant="static" value={selectedUser.type} onChange={(val) => setSelectedUser(
                                (prevState) => ({
                                    ...prevState,
                                    type: val
                                })
                            )}>
                                {Object.keys(TYPES).map((type) => (
                                    <Option key={type} value={type}>
                                        {TYPES[type]}
                                    </Option>
                                ))}
                            </Select>
                        </div>

                    </div>
                    <div className="flex flex-row items-center mb-3">
                        <Typography color='blue-gray' className='font-normal' variant='h6'>Is Active :</Typography>
                        <Checkbox color='blue' checked={selectedUser.is_active} onChange={(e) => setSelectedUser({ ...selectedUser, is_active: e.target.checked })} />
                    </div>

                    <Typography color='blue-gray' className='mb-3 font-normal' variant='h6'>Join Date : {new Date(selectedUser.date_joined).toLocaleString(undefined, {
                        year: "numeric",
                        month: "long",
                        day: "2-digit",
                        hour: "2-digit",
                        minute: "2-digit",
                    })}</Typography>
                </DialogBody>
                <DialogFooter>
                    <Button className='mx-1' color="red" onClick={() => setIsOpen(false)}>Cancel</Button>
                    <Button className='' color="blue" onClick={handleSave}>Save</Button>
                </DialogFooter>
            </Dialog>
        </div>


    );
};

export default ManageUsers;