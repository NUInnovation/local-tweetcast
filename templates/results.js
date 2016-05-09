<script src="//cdnjs.cloudflare.com/ajax/libs/d3/3.4.4/d3.min.js"></script>
<script src="d3pie.min.js"></script>
<script>
var pie = new d3pie("pieChart", {
	"header": {
		"title": {
			"text": "Political Preference of BLANK",
			"fontSize": 24,
			"font": "exo"
		},
		"subtitle": {
			"text": "BLANK Skews BLANK",
			"color": "#999999",
			"fontSize": 12,
			"font": "exo"
		},
		"titleSubtitlePadding": 9
	},
	"footer": {
		"color": "#999999",
		"fontSize": 10,
		"font": "open sans",
		"location": "bottom-left"
	},
	"size": {
		"canvasWidth": 590,
		"pieInnerRadius": "20%",
		"pieOuterRadius": "75%"
	},
	"data": {
		"sortOrder": "value-desc",
		"content": [
			{
				"label": "Republican",
				"value": 10,
				"color": "#ff0082"
			},
			{
				"label": "Democrat",
				"value": 20,
				"color": "#007cff"
			}
		]
	},
	"labels": {
		"outer": {
			"format": "none",
			"pieDistance": 32
		},
		"inner": {
			"format": "label-percentage1",
			"hideWhenLessThanPercentage": 3
		},
		"mainLabel": {
			"color": "#ffffff",
			"fontSize": 11
		},
		"percentage": {
			"color": "#ffffff",
			"decimalPlaces": 0
		},
		"value": {
			"color": "#adadad",
			"fontSize": 11
		},
		"lines": {
			"enabled": true
		},
		"truncation": {
			"enabled": true
		}
	},
	"effects": {
		"pullOutSegmentOnClick": {
			"effect": "linear",
			"speed": 400,
			"size": 8
		}
	},
	"misc": {
		"gradient": {
			"enabled": true,
			"percentage": 100
		}
	}
});
</script>
