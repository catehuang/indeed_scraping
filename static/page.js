window.onload=show_content;

// Ajax - all layouts are gone, difficult to read
function show_content(job, page_id)
{
    let xhr = new XMLHttpRequest();

    let content = "<div><h3 class=\"card-title text-center\">" + job.title + "</h3>" +
                  "<h4 class=\"card-subtitle mb-2 text-center text-info\">" + job.company_name + "</h4>" +
                  "<p class=\"card-text mb-2 text-center\">" + job.location + "</p>" +
                  "<a href=\"" + job.link + "\" type=\"button\" class=\"btn btn-warning\" target=\"_blank\">Apply</a>" +
                  "<pre class=\"text-break\">" + job.description + "</pre>" +
                  //"<p class=\"card-text text-break\">" + job.description + "</p>" +
                  "</div>";

    xhr.onreadystatechange = function ()
    {
        if (xhr.status === 0 || (xhr.status >= 200 && xhr.status < 400))
        {
            document.getElementById("job_content").innerHTML = content;
        }
    };
    xhr.open("GET", `${page_id}`, true);
    xhr.send();
}


