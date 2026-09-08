from flask import Flask, request, jsonify
import spi_ops, config, utilities, copy

app = Flask(__name__)

@app.route('/write_command', methods=['POST'])
def write_command():
    data = request.get_json()
    verify = request.args.get('verify', 'false').lower() == 'true'
    try:
        board_idx = data['board_idx']
        chip_letter = data['chip_letter']
        operation = data['operation']
        states = utilities.bin8_to_int(data['states'])
        my_list = []
        response = "" 
        cmd = spi_ops.Command()
        cmd.set_board_chip(board_idx, chip_letter, operation, 'w', states)
        my_list.append(copy.deepcopy(cmd))
        if verify:
            # cmd.set_board_chip(board_idx, chip_letter, operation, 'r', None)
            cmd.set_all_boards(operation, 'r', None)
            my_list.append(copy.deepcopy(cmd))
            response = utilities.convert_int_list_base(spi_ops.run(my_list, True),"bin")
        else:
            response = utilities.convert_int_list_base(spi_ops.run(my_list),"bin")
        return jsonify({"message": f"Write command {'w/' if verify else 'w/o'} verify executed successfully", "write_response": response}), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {str(e)}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid parameter value or type: {str(e)}"}), 400
    except AttributeError as e:
        return jsonify({"error": f"Configuration or module method error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error during output operation: {str(e)}"}), 500
   
@app.route('/read_command', methods=['POST']) 
def read_command():
    data = request.get_json()
    try:
        board_idx = data['board_idx']
        chip_letter = data['chip_letter']
        operation = data['operation']

        cmd = spi_ops.Command()
        cmd.set_board_chip(board_idx, chip_letter, operation, 'r', None)
        response = utilities.convert_int_list_base(spi_ops.run([cmd], True),"bin")
        return jsonify({"message": "Read command executed successfully", "read_response": response}), 200
    except KeyError as e:
        return jsonify({"error": f"Missing required parameter: {str(e)}"}), 400
    except (ValueError, TypeError) as e:
        return jsonify({"error": f"Invalid parameter value or type: {str(e)}"}), 400
    except AttributeError as e:
        return jsonify({"error": f"Configuration or module method error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"Unexpected error during output operation: {str(e)}"}), 500

@app.route('/std_diag', methods=['GET']) 
def std_diag():
    try:
        # response = utilities.convert_int_list_base(spi_ops.run([spi_ops.Command()], True),"bin")
        response = spi_ops.run([spi_ops.Command()], True)
        return jsonify({"message": "Standard Diagnostic command executed successfully", "std_diag_response": response}), 200

    except Exception as e:
        return jsonify({"error": f"Unexpected error during diagnostic operation: {str(e)}"}), 500

def start_flask_server ():
    app.run(debug=False, host=config.flask_ip, port=config.flask_port)
