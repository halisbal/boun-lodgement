import { apiService } from "../services/apiService";
import { useQuery } from "@tanstack/react-query";

const fetchApplications = async () => {
    return await apiService.get('/application/')

    const { data, status, error } = useQuery(["applicationDetail"], fetchApplications);
}

export default fetchApplications;