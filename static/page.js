window.onload=show_content;

// Ajax - all layouts are gone, difficult to read
function show_content(job, page_id)
{
    if (typeof job.title !== 'undefined')
    {
        let xhr = new XMLHttpRequest();

        xhr.onreadystatechange = function ()
        {
            if (xhr.status === 0 || (xhr.status >= 200 && xhr.status < 400))
            {
                document.getElementById("job_title").innerText = job.title;
                document.getElementById("job_company_name").innerText = job.company_name;
                document.getElementById("job_location").innerText = job.location;
                document.getElementById("job_link").setAttribute("href", job.link);
                document.getElementById("job_description").innerText = job.description;
            }
        };
        xhr.open("GET", `${page_id}`, true);
        xhr.send();
    }
}


// add/remove the active class for further customization
$(function()
{
    $('.list-group li').click(function(e)
    {
        e.preventDefault();
        $that = $(this);
        $that.parent().find('li').removeClass('active');
        $that.addClass('active');
    });
})


/* use iframe but: because an ancestor violates the following Content Security Policy directive: "frame-ancestors 'self
function show_content(job, page_id)
{
    document.getElementById("job_content").setAttribute("src", job.link);
}
*/



