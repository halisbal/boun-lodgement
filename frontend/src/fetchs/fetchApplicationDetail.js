import {apiService} from '../services/apiService';

const fetchApplicationDetail = async (id) => {
    return await apiService.get(`/application/${id}`);
}

export default fetchApplicationDetail;