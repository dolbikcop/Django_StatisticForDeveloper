new Vue(
    {
        el: '#vacancies_app',
        data: {
            vacancies: []
        },
        created: function () {
            const vm = this;
            axios.get("/api/vacancies")
                .then(function (response) {
                    vm.vacancies = response.data;
                })
        }
    }
)