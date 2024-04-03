import $ from 'jquery';
export const getAIMessage = async (userQuery) => {
  var message = "";
    function sendQuestionToBackend(userQuery) {
      var result = "";
    // Function returns the product of a and b
      $.ajax({
        type: 'POST',
        url: "http://127.0.0.1:5000/api",
        contentType: 'application/json', 
        data: JSON.stringify({ 'value': userQuery}),
        async: false,
        success:function(data) {
          result = data;
       },
        timeout: 0
      });
      return result;
    }

    function obtainContent(backendContent) {
      message = 
        {
          role: "assistant",
          content: backendContent['value']
        };
      return message;
    }
    var new_result = sendQuestionToBackend(userQuery);
    var new_msg = obtainContent(new_result);
    
    return new_msg;
};
