import { List, ListItem, Card, Typography } from "@material-tailwind/react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import fetchApplications from "../fetches/fetchApplications";

export default function ListApplicationsPage() {

    const { data, status, error } = useQuery(["applicationList"], fetchApplications);
    if (status === 'loading') {
        return <div>Loading...</div>
    }
    if (status === 'error') {
        return <div>Error: {error.message}</div>
    }
    console.log(data);



    return (
        <div className="h-screen bg-gray-100 mx-auto w-full">
            <div className="p-14">
                <div className="p-6">
                    <Typography 
                        color="blue-gray"
                        className=""
                        variant="h4"
                    >My Applications</Typography>
                </div>
                <div className="flex justify-start p-6">
                    <Card className="w-10/12 ">
                        <List>
                            {data?.map((application) => {

                                var statusColor = "";
                                if (application.status === 'In Progress') {
                                    statusColor = 'text-yellow-700 font-normal'
                                } else if (application.status === 'Approved') {
                                    statusColor = 'text-green-500 font-normal'
                                } else {
                                    statusColor = 'text-red-500 font-normal'
                                }

                                return (
                                    <Link to={`/application/${application.id}`}>
                                        <ListItem key={application.id}>
                                            <div className="flex justify-between w-full">
                                                <div className="flex flex-col">
                                                    <Typography color="blue-gray" className="font-normal">{application.queue.lodgement_type} - {application.queue.personel_type} - {application.queue.lodgement_size}</Typography>
                                                </div>
                                                <div>
                                                    <Typography className={statusColor}>{application.status}</Typography>
                                                </div>
                                            </div>
                                        </ListItem>
                                    </Link>)
                            }
                            )}
                        </List>
                    </Card>
                </div>

            </div>
        </div >


    );
}