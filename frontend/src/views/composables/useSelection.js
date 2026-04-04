export const useSelection = (selectedActivities) => {

  const isSelected = (activity) => {
    return selectedActivities.value.some(
      (selectedActivity) => selectedActivity.activity_id === activity.activity_id
    );
  };

  const toggle = (activity) => {
    const index = selectedActivities.value.findIndex(
      (selectedActivity) => selectedActivity.activity_id === activity.activity_id
    );

    if (index > -1) {
      selectedActivities.value.splice(index, 1);
    } else {
      selectedActivities.value.push(activity);
    }
  };

  const clear = () => {
    selectedActivities.value = [];
  };

  const toggleAll = (activities) => {
    if (selectedActivities.value.length === activities.length) {
      selectedActivities.value = [];
    } else {
      selectedActivities.value = activities.map(activity => ({ ...activity }));
    }
  };

  return {
    isSelected,
    toggle,
    clear,
    toggleAll
  }
};
