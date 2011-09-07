Django application which manage to generation and validation of unique keys(tokens).

It is possible to manager permission assign to those keys. 

## Install

    cd [path_to_tokit]/
    python setup.py install
    
Add it in your django settings INSTALLED_APPS

In your code

    from tokit.decorators import validate_token
    @validate_token()
    def get_what_i_want(request):
        return data
        
This will first validate that there is a api_key in the url or in the header and that the key is valid.
