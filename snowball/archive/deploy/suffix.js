var c_media = window.matchMedia('(max-width: 1023px)');
var tdat_name = []; var tdat_scale = []; var tdat_caps = []; var tdat_price = []; var tdat_perf = []; var tdat_color = [];
var map_type; var market_type; var option_type; var map_key;

var map_layout = {
    height: 690,
    margin:{l:2,r:2,t:2,b:25}
};
var map_option = {
    displayModeBar:false,
    responsive:true,
    showTips:false
};

function setSearch(key){
	$('.map-search').empty();
	$('.map-search').append('<option></option>');
	for (var n = 0; n < tdat_ids[key].length; n++){
		$('.map-search').append('<option>' + tdat_ids[key][n] + '</option>');
	}
}

function search_top(__group__){
  var elems = $('.slicetext');
	var clicker = null;
	var name = '';
	for (var n = 0; n < elems.length; n++){
		name = $(elems[n]).text();
		if (name == __group__){
			clicker = $(elems[n]).parent().get(0);
			break;
		}
	}
	if (clicker == null) {return;}
	if (document.createEvent) {
			var event = document.createEvent('MouseEvents');
			event.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
			!clicker.dispatchEvent(event);
	} else if (link.fireEvent) {
		!clicker.fireEvent('onclick');
	}
}

function search_asset(__asset_name){
	var elems = $('.slicetext');
	var clicker = null;
	for (var n = 0; n < elems.length; n++){
		var name = $(elems[n]).text();
    if ((name.includes(__asset_name)) && (name.slice(0, __asset_name.length) == __asset_name)){
      var leftover = name.slice(__asset_name.length, name.length)
      var tail_cnt = 0;
      var digits = leftover.match(/\d/g);
      if (digits != null){
  			tail_cnt += digits.length;
  		}
      if (leftover.includes('-')){ tail_cnt += 1 }
      if (leftover.includes('.')){ tail_cnt += 1 }
      if (leftover.includes('%')){ tail_cnt += 1 }
      if ((leftover.length - tail_cnt) == 0){
        clicker = $(elems[n]).parent().get(0);
  		  break;
      }
    }
	}
	if (clicker == null){
		return
	}
	if (document.createEvent) {
			var event = document.createEvent('MouseEvents');
			event.initMouseEvent('click', true, true, window, 0, 0, 0, 0, 0, false, false, false, false, 0, null);
			!clicker.dispatchEvent(event);
	} else if (link.fireEvent) {
		!clicker.fireEvent('onclick');
	}
}

function treemap(key){
  var _t, _u, _treemap;
  tdat_name = []; tdat_scale = []; tdat_caps = []; tdat_price = []; tdat_perf = []; tdat_color = [];

  tdat_labels[key].forEach(function(code){
	  tdat_name.push(tdat_frm[code]['종목명']);
	  tdat_scale.push(tdat_frm[code]['크기']);
	  tdat_caps.push(tdat_frm[code]['시가총액']);
	  tdat_price.push(tdat_frm[code]['종가']);
	  tdat_perf.push(tdat_frm[code][option_type]);
	  tdat_color.push(tdat_frm[code]['C' + option_type]);
  });
  _t = (option_type == 'PER' || option_type == 'PBR') ? option_type : '수익률';
  _u = (option_type == 'PER' || option_type == 'PBR') ? '' : '%';

  _treemap={
    type:'treemap',
    branchvalues:'total',
    labels:tdat_name,
    parents:tdat_covers[key],
    values:tdat_scale,
    ids:tdat_name,
    meta:tdat_caps,
    customdata:tdat_price,
    text:tdat_perf,
	textposition:'middle center',
    textfont:{
      family:'NanumGothic, Nanum Gothic, monospace',
      color:'#ffffff'
    },
    texttemplate: '%{label}<br>%{text}' + _u,
    hovertemplate: '%{label}<br>시총: %{meta}<br>종가: %{customdata}<br>' + _t + ': %{text}' + _u + '<extra></extra>',
	hoverlabel: {
      font: {
        family: 'NanumGothic, Nanum Gothic, monospace',
        color: '#ffffff'
      }
    },
	opacity: 0.9,
    marker: {
      colors: tdat_color,
      visible: true
    },
    pathbar: {'visible': true}
  }
  Plotly.newPlot('myMap', [_treemap], map_layout, map_option);
}
