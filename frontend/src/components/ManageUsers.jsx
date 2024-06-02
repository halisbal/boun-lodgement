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

} from "@material-tailwind/react";
import { useQuery } from "@tanstack/react-query";
import { useState, useMemo } from "react";
import { apiService } from "../services/apiService";
import { defer } from "react-router-dom";


const ROLES = {
    1:"User",
    2:"Manager",
    3:"Admin"
}
const ROLES_REVERSE = {
    "User":1,
    "Manager":2,
    "Admin":3
}

const TYPES = {
    1:"Akademik",
    2:"İdari",
    3:"Görevli"
}
const TYPES_REVERSE = {
    "Akademik":1,
    "İdari":2,
    "Görevli":3
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

const TABLE_HEAD = ["Id", "Name", "Email", "Role", "Type", "Is Active", "Join Date", ""];

const ManageUsers = () => {
    const { data: users, isLoading, error } = useQuery(["all-users"], () => apiService.get(`/auth/user/`));
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage] = useState(6);
    const [activeTab, setActiveTab] = useState("all");
    const [sortConfig, setSortConfig] = useState({ key: "id", direction: "ascending" });
    const [searchQuery, setSearchQuery] = useState("");
    const [isOpen, setIsOpen] = useState(false);
    const [selectedUser, setSelectedUser] = useState({});

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
        setSelectedUser(user);
        setIsOpen(true);
    }

    const handleSave = () => {
        console.log("Save");
        setIsOpen(false);
    }

    if (isLoading) {
        return <div>Loading...</div>;
    }

    if (error) {
        return <div>Error: {error.message}</div>;
    }

    return (
        <div className="flex justify-center">
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
            <Dialog size='sm' open={isOpen} handler={setIsOpen}>
                    <DialogHeader>Lodgement Info</DialogHeader>
                    <DialogBody >
                        <Typography color='blue-gray' className='mb-2' variant='h6'>Id : {selectedUser.id}</Typography>
                    </DialogBody>
                    <DialogFooter>
                        <Button className='mx-1' color="red" onClick={()=> setIsOpen(false)}>Cancel</Button>
                        <Button className=''color="blue" onClick={handleSave}>Save</Button>
                    </DialogFooter>
                </Dialog>
        </div>


    );
};

export default ManageUsers;