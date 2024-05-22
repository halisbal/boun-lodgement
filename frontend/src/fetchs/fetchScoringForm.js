import { apiService } from "../services/apiService";

const fetchScoringForm = async (data) => {
    return await apiService.get("/scoring_form/");
}

export default fetchScoringForm;