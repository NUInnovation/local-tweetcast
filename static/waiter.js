$(document).ready(function () {
 worker()
});

function worker() {
  var checkurl = '/checkincache/' + $('#city').html();
   $.get(checkurl, function (res){
     console.log(res);
     setTimeout(worker, 1000);
     if (res == 'Yes') {
       window.location.replace('/results/' + $('#city').html());
     }
   });
}
