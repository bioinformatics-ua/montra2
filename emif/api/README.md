The plan is migrate all the RESTFull methods to this component.
We want to harmonize the data, so when develop a new service respecting the following methodology:

base url/api/< component >/< service name >

The organization of this component will be

api -> < component name >_api -> 2 files (serializers and views)