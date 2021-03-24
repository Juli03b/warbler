async function likeOrDislike(msgId){
    const res = await axios.post(`/users/add_like/${msgId}`);

    if (res.data.status === 404)
        return false;
    else
        return res.data.status;
    
}

$('.list-group').on('submit', 'form' ,async function(evt){
    evt.preventDefault();

    const btn = $(evt.target).children().eq(0)
    const msgId = $(evt.target).data('msg-id')
    const status = await likeOrDislike(msgId);

    if (status === 'liked'){
        $(btn).removeClass('far');
        $(btn).addClass('fas');
        $(btn).removeClass('btn-primary');
        $(btn).addClass('btn-secondary');    
    }else{
        $(btn).removeClass('fas');
        $(btn).addClass('far');    
        $(btn).removeClass('btn-secondary');
        $(btn).addClass('btn-primary');
    }
})