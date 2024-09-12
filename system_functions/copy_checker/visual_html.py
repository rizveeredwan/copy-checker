space_characters = [' ', '\t']


def show_matched_code_with_col(source_code=[], setblueprint={}):
    global space_characters
    _string = ""
    for i in range(0, len(source_code)):
        for j in range(0, len(source_code[i])):
            if source_code[i][j] in space_characters:
                _string +='&nbsp;'
                continue
            if setblueprint.get(i) is not None and setblueprint[i].get(j) is not None:
                _string += '<span style="color:red;">'+source_code[i][j]+'</span>'
            else:
                _string += '<span>'+source_code[i][j]+'</span>' 
        _string += '<span><br>'+'</span>' 
    return _string  


def show_matched_code_with_col_using_arr_data(tagged_source_code=[]):
    global space_characters
    _string = ""
    for i in range(0, len(tagged_source_code)):
        if tagged_source_code[i][0] in space_characters:
            _string +='&nbsp;'
            continue
        if tagged_source_code[i][1] == -1: # not matched
            _string += '<span style="color:black;">' + tagged_source_code[i][0] + '</span>'
        else:
            _string += '<span style="color:red;">'+tagged_source_code[i][0]+'</span>'
    return _string


def prepapre_html_page(json_codes={}, i=0, j=1):
    _string = "<!DOCTYPE html>"
    _string += '<html lang="en">'
    _string += '<head>'
    _string += '<meta charset="UTF-8">'
    _string += '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    _string += '<title>Copy Statistics for file '+str(i+1)+' and file ' + str(j+1)+ '</title>'
    _string += '<style>'
    _string += 'body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;}'
    _string += 'header {background-color: #333; color: #fff; padding: 1em; text-align: center;}'
    _string += 'section { max-width: 800px; margin: 20px auto; padding: 20px; background-color: #fff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);}'
    _string += 'footer { background-color: #333; color: #fff; padding: 1em; text-align: center;}'
    _string += '</style>'
    _string += '</head>'
    _string += '<body>'
    _string += '<h1>Code Found in File '+ str(i+1) + '</h1>'
    _string += '<div>'
    _string += json_codes[i]['match_status'][j][3] # just html string 
    _string += '</div>'
    _string += '<h1>Code Found in File '+ str(j+1) + '</h1>'
    _string += '<div>'
    _string += json_codes[j]['match_status'][i][3] # just html string 
    _string += '</div>'
    _string += '</body>'
    _string += '</html>'
    return _string 


def generate_visual_html_for_client(file1_name="", file2_name="", alpha="", level_threshold="", sim_score=0, tag_file1_code_arr=[], tag_file2_code_arr=[]):
    _string = "<!DOCTYPE html>"
    _string += '<html lang="en">'
    _string += '<head>'
    _string += '<meta charset="UTF-8">'
    _string += '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
    _string += '<title>Copy Statistics for file ' + file1_name + ' and file ' + file2_name + '</title>'
    _string += '<style>'
    _string += 'body { font-family: Arial, sans-serif; margin: 0; padding: 0; background-color: #f4f4f4;}'
    _string += 'header {background-color: #333; color: #fff; padding: 1em; text-align: center;}'
    _string += 'section { max-width: 800px; margin: 20px auto; padding: 20px; background-color: #fff; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);}'
    _string += 'footer { background-color: #333; color: #fff; padding: 1em; text-align: center;}'
    _string += '</style>'
    _string += '</head>'
    _string += '<body>'
    _string += 'Metadata: ' + 'Alpah = ' + str(alpha) + " " + 'Level Threshold ' + str(level_threshold) + "<br>"
    _string += 'Similarity Score ' + str(sim_score) + '<br>'
    source_code_string1 = show_matched_code_with_col_using_arr_data(tagged_source_code=tag_file1_code_arr)
    source_code_string2 = show_matched_code_with_col_using_arr_data(tagged_source_code=tag_file2_code_arr)
    _string += '<h1>Code Found in File ' + file1_name + '</h1>'
    _string += '<div>'
    _string += source_code_string1  # just html string
    _string += '</div>'
    _string += '<h1>Code Found in File ' + file2_name + '</h1>'
    _string += '<div>'
    _string += source_code_string2  # just html string
    _string += '</div>'
    _string += '</body>'
    _string += '</html>'
    return _string


def write_into_html_file(html_string="", file_name=""):
    with open(file_name, 'w') as f:
        f.write(html_string)