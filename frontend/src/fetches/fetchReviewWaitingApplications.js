import { apiService } from "../services/apiService";

const fetchReviewWaitingApplications = async () => {
    return await apiService.get("/application/waiting-for-review/");

};

export default fetchReviewWaitingApplications;