import {apiService} from "./apiService";

const getLodgementList = async () => {
  try {
    const response = await apiService.get("/lodgement/");
    return response;
  } catch (error) {
    console.error(error);
    return null;
  }
}

export default { getLodgementList };
    