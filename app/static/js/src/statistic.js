/* ------------------------------- admin-statistic ------------------------------- */

/* -------------------- charts -------------------- */

$.ajax({
	type: 'POST',

})

var ctx1 = document.getElementById('marksPieChart').getContext('2d');

var marksPieChart = new Chart(ctx1, {
	type: 'pie',
	data: {
		labels: [
			'Отлично',
			'Хорошо',
			'Норма'
		],
		datasets: [{
			data: [ 125, 214, 24 ],
			backgroundColor: [
				'rgba(255, 99,  132, 0.6)',
				'rgba(54,  162, 235, 0.6)',
				'rgba(153, 102, 255, 0.6)'
			],
			borderColor: [
				'rgba(255, 99, 132, 1)',
				'rgba(54, 162, 235, 1)',
				'rgba(153, 102, 255, 1)'
			],
			hoverBackgroundColor: [
				'rgba(255, 99,  132, 0.8)',
				'rgba(54,  162, 235, 0.8)',
				'rgba(153, 102, 255, 0.8)'
			],
			borderWidth: 1,
			weight: 100,
		}],
	},
	options: {
		layout: {
			padding: {
				left:   0,
				right:  0,
				top:    10,
				bottom: 20
			},
		},
		rotation: 1.5 * Math.PI,
	},
});
