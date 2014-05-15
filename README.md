A Django application for the management, generation and validation of unique REST API keys (tokens).

Also lets you specify permissions for each individual key, giving access only to certain portions
of your API to specific API consumers. 

## Install

    cd [path_to_tokit]/
    python setup.py install
    
Add tokit to the list of INSTALLED_APPS in your settings.py file.

## Usage

In your code:

    from tokit.decorators import validate_token
    
    # this decorator will block access if a valid api_key is not provided
    # in the request http header or get parameter
    @validate_token()
    def get_what_i_want(request):
        return data

	# if a list of permissions is given, tokit will also block the call if the provided
	# api_key does not have all required permissions
	@validate_token(permissions=["very_sensitive_endpoint"])
    def get_that_other_thing(request):
        return data

API keys and permissions can be managed via the admin interface if it is enabled in
your Django settings file.
