<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;

class SearchController extends Controller
{
    public function search(Request $request)
    {

        $name = $request->name;
        $freeText = $request->text;
        $location = $request->location;

        $name = str_replace("'", "", $name);
        $freeText = str_replace("'", "", $freeText);
        $location = str_replace("'", "", $location);

        $name = str_replace('"', '', $name);
        $freeText = str_replace('"', '', $freeText);
        $location = str_replace('"', '', $location);

        $name = trim($name);
        $freeText = trim($freeText);
        $location = trim($location);

        if (empty($freeText)) {
            return redirect()->back()->with(['msg' => 'Please enter something to look for']);
        }
        $output = "";
        if (!empty($name) || !empty($freeText) || !empty($location)) {
            $pythonScriptPath = env('PY_SCRIPT_PATH', '');
            $pythonScriptName = env('PY_SCRIPT_NAME', '');
            $pythonCommand = env('PY_COMMAND', '');
            if (!empty($pythonScriptPath) && !empty($pythonScriptName) && !empty($pythonCommand)) {
                $str = "$pythonCommand $pythonScriptPath/$pythonScriptName '$name' '$freeText' '$location' 2>&1";
                $command = escapeshellcmd($str);
                $output = shell_exec($str);
            }
        } else {
            return redirect()->back()->with(['msg' => 'Please enter something in the search box']);
        }
        //dd($output);
        $data = json_decode(rtrim($output, '\n'), true);
        if (empty($data)) {
            $data = [];
        }
        $images = ["img/explorer/1.png", "img/explorer/2.png", "img/explorer/3.png", "img/explorer/4.png",
            "img/explorer/5.png", "img/explorer/6.png"];

        $query = [
            'name' => $request->name,
            'text' => $request->text,
            'location' => $request->location
        ];
        //dd($data);
        return view('listings', ['data' => $data, 'images' => $images, 'query' => $query]);
    }
}
