import { useQuery } from "@tanstack/react-query";
import { apiService } from "../services/apiService";
import { Card, CardBody, CardHeader, Typography } from "@material-tailwind/react";


const HomePage = () => {

  const { data: announcements, isLoading, error } = useQuery(["announcements"], () => apiService.get("/announcement/"));

  if (isLoading) {
    return <div>Loading...</div>;
  }
  if (error) {
    return <div>Error: {error.message}</div>;
  }

  console.log("data : ", announcements);


  return (
    <div className="container mx-auto p-6">
      <Typography variant="h2" color="blue-gray" className="mb-8 text-center font-bold">
        Announcements
      </Typography>
      <div className="grid grid-cols-1 gap-6">
        {announcements.map((announcement) => (
          <Card key={announcement.id} className="shadow-lg rounded-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader color="blue" className="text-white rounded-t-lg p-4">
              <Typography variant="h5" className="font-semibold">
                {announcement.title}
              </Typography>
              <Typography variant="small" className="text-white opacity-80">
                {new Date(announcement.created_at).toLocaleDateString()}
              </Typography>
            </CardHeader>
            <CardBody className="rounded-b-lg p-4">
              <Typography className="text-blue-500 hover:text-blue-700 transition-colors duration-300">
                <a href={announcement.content} target="_blank" rel="noopener noreferrer">
                  {announcement.content}
                </a>
              </Typography>
            </CardBody>
          </Card>
        ))}
      </div>
    </div>
  );
};

export default HomePage;
