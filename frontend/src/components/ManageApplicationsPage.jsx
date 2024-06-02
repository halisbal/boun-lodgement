import { List } from "@material-tailwind/react";
import { useQuery } from "@tanstack/react-query";
import { apiService } from "../services/apiService";
import { useState } from "react";
import { Dialog, DialogBody, DialogFooter, DialogHeader, Input, Typography, Tooltip } from "@material-tailwind/react";
import { EyeIcon } from "@heroicons/react/20/solid";
import { IconButton } from "@material-tailwind/react";
import { useNavigate } from "react-router-dom";
import fetchReviewWaitingApplications from "../fetches/fetchReviewWaitingApplications";

const TABLE_HEADERS = ["Id", "Email", "Queue", "Application Date",""];

const ManageApplicationsPage = () => {

    const navigate = useNavigate();

    const [isOpen, setIsOpen] = useState(false);
    const [selectedApplication, setSelectedApplication] = useState({});


    const { data: applications, error, isLoading } = useQuery(['review-applications'], fetchReviewWaitingApplications);

    console.log("applications : ", applications)

    if (isLoading) {
        return <div>Loading...</div>
    }

    if (error) {
        return <div>Error: {error.message}</div>
    }

    const handleDetailClick = (id) => {
        navigate(`/manage-application-detail/${id}`);
    }

    return (

        <div className="flex justify-center align-middle">


            <div className="w-3/4 ">
                <Typography
                    color="blue-gray"
                    className="my-8 mt-12"
                    variant="h4"
                >Review Pending Applications
                </Typography>
                <table className="mt-4 w-full min-w-max table-auto text-left">
                    <thead>
                        <tr className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50">

                            {TABLE_HEADERS.map((head, index) => (
                                <th key={head} className="cursor-pointer border-y border-blue-gray-100 bg-blue-gray-50/50 p-4 transition-colors hover:bg-blue-gray-50">
                                    <Typography variant="small" color="blue-gray" className="flex items-center justify-between gap-2 font-normal leading-none opacity-70">
                                        {head}
                                    </Typography>
                                </th>
                            ))}

                        </tr>
                    </thead>
                    <tbody>
                        {applications.map((application, index) => {
                            const isLast = index === applications.length - 1;
                            const classes = isLast
                                ? "p-4"
                                : "p-4 border-b border-blue-gray-50";


                            return (
                                <tr key={application.id} onDoubleClick={() => handleDetailClick(application.id)}>
                                    <td className={classes}>
                                        <div className="flex items-center gap-3">
                                            <Typography
                                                variant="small"
                                                color="blue-gray"
                                                className="font-normal"
                                            >
                                                {application.id}
                                            </Typography>
                                        </div>
                                    </td>
                                    <td className={classes}>
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {application.user.email}
                                        </Typography>
                                    </td>


                                    <td className={classes}>
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {application.queue.personel_type} - {application.queue.lodgement_type} - {application.queue.lodgement_size}
                                        </Typography>
                                    </td>
                                    <td className={classes}>
                                        <Typography
                                            variant="small"
                                            color="blue-gray"
                                            className="font-normal"
                                        >
                                            {application.created_at}
                                        </Typography>
                                    </td>

                                    <td className={classes}>
                                        <Tooltip content="See Details">
                                            <IconButton variant="text" onClick={() => handleDetailClick(application.id)}>
                                                <EyeIcon className="h-4 w-4" />
                                            </IconButton>
                                        </Tooltip>
                                    </td>
                                </tr>);
                        })}

                    </tbody>

                </table>
            </div>

        </div>

    );

}

export default ManageApplicationsPage; 