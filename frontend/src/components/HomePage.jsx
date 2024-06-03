import { useQuery } from "@tanstack/react-query";
import { apiService } from "../services/apiService";
import { Card, CardBody, CardHeader, Typography } from "@material-tailwind/react";
import FAQ from "./FAQPage";
import DOMPurify from "dompurify";


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
      <Typography variant="h3" color="blue-gray" className="mb-8 font-bold">
        Announcements
      </Typography>
      <div className="grid grid-cols-1 gap-6">
        {announcements.map((announcement) => (
          <Card key={announcement.id} className="shadow-lg rounded-lg hover:shadow-xl transition-shadow duration-300">
            <div className="p-6">
              <Typography variant="h5" color="blue-gray" className="font-normal">
                {announcement.title}
              </Typography>
              <Typography variant="small" className="">
                {new Date(announcement.created_at).toLocaleDateString()}
              </Typography>
            </div>

            <CardBody className="rounded-b-lg p-4"> 
              <Typography className="">
                <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(announcement.content) }}>
                </div>
              </Typography>
            </CardBody>
          </Card>
        ))}
      </div>

      <FAQ />
      
    </div>
  );
};

export default HomePage;
