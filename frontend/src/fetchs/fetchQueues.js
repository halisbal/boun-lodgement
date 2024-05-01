import { apiService } from "../services/apiService"

const fetchQueues = async () => {
    return await apiService.get('/queue/')
}

export default fetchQueues;