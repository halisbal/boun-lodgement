import { apiService } from "../services/apiService";
import { useQuery } from "@tanstack/react-query";
import { useParams, useNavigate } from "react-router-dom";
import { useState } from "react";
import { Button, Card, CardBody, CardFooter, CardHeader, Textarea, Typography, Alert } from "@material-tailwind/react";
import MyAlert from "./MyAlert";


const ManageApplicationsDetail = () => {

    const [reason, setReason] = useState('');
    const [alert, setAlert] = useState({ message: '', color: 'success', visible: false });

    const { id } = useParams();
    const { data: application, isLoading, error } = useQuery(["application", id], () => apiService.post(`/application/get/`, { application_id: id }));

    const navigate = useNavigate();

    if (isLoading) {
        return <div>Loading...</div>;
    }
    if (error) {
        return <div>Error: {error.message}</div>;
    }

    console.log("data : ", application);

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


    const handleApprove = () => {

        apiService.post(`/application/review/`, { application_id: id, system_message: reason, status: 3 }).then(res => {
            navigate("/manage-applications");
            showAlert("Application approved successfully");
        }).catch(err => {
            showAlert("An error occured while approving the application : " + err.message, "error");
        });

    }

    const handleReject = () => {

        apiService.post(`/application/review/`, { application_id: id, system_message: reason, status: 4 }).then(res => {
            navigate("/manage-applications");
            showAlert("Application rejected successfully", "success");
        }).catch(err => {
            showAlert("An error occured while rejecting the application : " + err.message, "error");
        });

    }

    const handleReupload = () => {

        apiService.post(`/application/review/`, { application_id: id, system_message: reason, status: 5 }).then(res => {
            navigate("/manage-applications");
            showAlert("Application status set to re-upload successfully", "success");
        }).catch(err => {
            showAlert("An error occured while setting the application status to re-upload : " + err.message, "error");
        });

    }

    return (
        <div className="bg-gray-200">
            {alert.visible && <MyAlert message={alert.message} type={alert.type} onClose={closeAlert} visible={alert.visible} />}
            <Card className="m-8">
                <CardBody>
                    <Typography
                        color="blue-gray"
                        className="mb-2"
                        variant="h4"

                    >Details</Typography>
                    <div className="mb-4">
                        <p><strong>Status:</strong> {application.status}</p>
                        <p><strong>Role:</strong> {application.user.role}</p>
                        <p><strong>Type:</strong> {application.user.type}</p>
                        <p><strong>Email:</strong> {application.user.email}</p>
                        <p><strong>Application Date:</strong> {new Date(application.created_at).toLocaleString(undefined, { year: "numeric", month: "long", day: "2-digit", hour: "2-digit", minute: "2-digit" })}</p>
                        <p><strong>Lodgement Type:</strong> {application.queue.lodgement_type}</p>
                        <p><strong>Personel Type:</strong> {application.queue.personel_type}</p>
                        <p><strong>Lodgement Size:</strong> {application.queue.lodgement_size}</p>
                        <p><strong>Rank:</strong> {application.rank}</p>
                        <p><strong>Total Points:</strong> {application.total_points}</p>
                        <p><strong>Estimated Availability:</strong> {application.estimated_availability}</p>
                    </div>

                    <Typography
                        color="blue-gray"
                        className="mb-2"
                        variant="h4"

                    >Uploaded Documents</Typography>
                    <ul className="mb-4">
                        {application.documents.length == 0 ? "No uploaded documents" : application.documents.map(doc => (
                            <li key={doc.id}>
                                <p><strong>{doc.document.name}:</strong></p>
                                {doc.file && <a href={doc.file} target="_blank" rel="noopener noreferrer" className="text-blue-500">View Document</a>}
                            </li>
                        ))}
                    </ul>

                    <Typography
                        color="blue-gray"
                        className="mb-2"
                        variant="h4"

                    >Scroring Form</Typography>
                    <ul className="mb-4">
                        {application.scoring_form.items.map(item => (
                            <li key={item.id}>
                                <p><strong>{item.label}:</strong> {item.answer ? item.answer.value : 'N/A'}</p>
                                <p className="text-sm text-gray-500">{item.caption}</p>
                            </li>
                        ))}
                    </ul>

                    <Textarea
                        color="blue"
                        label="Review Message"
                        value={reason}
                        onChange={(e) => setReason(e.target.value)}
                        className="mb-4"
                    />
                </CardBody>
                <CardFooter className="flex justify-end">
                    <Button color="red" className="mr-2" onClick={handleReject}>Reject</Button>
                    <Button color="amber" className="mr-2" onClick={handleReupload}>Re-Upload</Button>
                    <Button color="green" onClick={handleApprove} className="mr-2">Approve</Button>

                </CardFooter>
            </Card>

        </div>
    );
};

export default ManageApplicationsDetail;