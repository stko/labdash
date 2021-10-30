"use strict";

let port;
let reader;
let inputDone;
let outputDone;
let inputStream;
let outputStream;



document.addEventListener("DOMContentLoaded", () => {
	const log = document.getElementById("log");
	const butConnect = document.getElementById("butConnect");

	butConnect.addEventListener("click", clickConnect);

	// CODELAB: Add feature detection here.
	const notSupported = document.getElementById("notSupported");
	notSupported.classList.toggle("hidden", "serial" in navigator);

});

/**
 * @name connect
 * Opens a Web Serial connection to a micro:bit and sets up the input and
 * output stream.
 */
async function connect() {
  // CODELAB: Add code to request & open port here.
  // - Request a port and open a connection.
  port = await navigator.serial.requestPort();
  // - Wait for the port to open.
  await port.open({ baudRate: 9600 });

  // CODELAB: Add code setup the output stream here.
  const encoder = new TextEncoderStream();
  outputDone = encoder.readable.pipeTo(port.writable);
  outputStream = encoder.writable;

  // CODELAB: Send CTRL-C and turn off echo on REPL

  // CODELAB: Add code to read the stream here.
  let decoder = new TextDecoderStream();
  inputDone = port.readable.pipeTo(decoder.writable);
  inputStream = decoder.readable
    .pipeThrough(new TransformStream(new LineBreakTransformer()))
    .pipeThrough(new TransformStream(new JSONTransformer()));

  reader = inputStream.getReader();
  readLoop();
}

/**
 * @name disconnect
 * Closes the Web Serial connection.
 */
async function disconnect() {


  // CODELAB: Close the input stream (reader).
  if (reader) {
    await reader.cancel();
    await inputDone.catch(() => {});
    reader = null;
    inputDone = null;
  }

  // CODELAB: Close the output stream.
  if (outputStream) {
    await outputStream.getWriter().close();
    await outputDone;
    outputStream = null;
    outputDone = null;
  }

  // CODELAB: Close the port.
  await port.close();
  port = null;
}

/**
 * @name clickConnect
 * Click handler for the connect/disconnect button.
 */
async function clickConnect() {
  // CODELAB: Add disconnect code here.
  if (port) {
    await disconnect();
    toggleUIConnected(false);
    return;
  }

  // CODELAB: Add connect code here.
  await connect();
  vm = new shine.VM(env);
  //vm.load('./lua/light-seconds.lua.json');
  vm.load('./lua/my_first_oobd.lua.json');
  
  
  toggleUIConnected(true);
}

/**
 * @name readLoop
 * Reads data from the input stream and displays it on screen.
 */
async function readLoop() {
  // CODELAB: Add read loop here.
  while (true) {
    const { value, done } = await reader.read();
    if (value && value.button) {
      buttonPushed(value);
    } else {
      log.textContent += value + "\n";
    }
    if (done) {
      console.log("[readLoop] DONE", done);
      reader.releaseLock();
      break;
    }
  }
}

/**
 * @name writeToStream
 * Gets a writer from the output stream and send the line
 * @param  {...string} lines line to send
 */
function writeToStream(line) {
	// CODELAB: Write to output stream
	const writer = outputStream.getWriter();
	console.log("[SEND]", line);
	writer.write(line);
	writer.releaseLock();
}


/**
 * @name LineBreakTransformer
 * TransformStream to parse the stream into lines.
 */
class LineBreakTransformer {
  constructor() {
    // A container for holding stream data until a new line.
    this.container = "";
  }

  transform(chunk, controller) {
    // CODELAB: Handle incoming chunk
    this.container += chunk;
    const lines = this.container.split("\r\n");
    this.container = lines.pop();
    lines.forEach(line => controller.enqueue(line));
  }

  flush(controller) {
    // CODELAB: Flush the stream.
    controller.enqueue(this.container);
  }
}

/**
 * @name JSONTransformer
 * TransformStream to parse the stream into a JSON object.
 */
class JSONTransformer {
  transform(chunk, controller) {
    // CODELAB: Attempt to parse JSON content
    try {
      controller.enqueue(JSON.parse(chunk));
    } catch (e) {
      controller.enqueue(chunk);
    }
  }
}


function toggleUIConnected(connected) {
	let lbl = "Connect";
	if (connected) {
	  lbl = "Disconnect";
	}
	butConnect.textContent = lbl;
  }
  


var env = {
	speedOfLight: 299792458,
	distanceToMoon: 384400000,
	log: function log (message) {
		console.log('Message from Lua: ' + message);
	},

	openPageCall: function openPageCall (pageName) {
		console.log('openPageCall from Lua:');
/* 		try {
			core.transferMsg(new Message(myself, UIHandlerMailboxName,
					new Onion("" + "{'type':'" + CM_PAGE + "',"
							+ "'owner':'" + myself.getId() + "',"
							+ "'name':'" + getString(0) + "'}")));
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}
 */		return 1;
	},

	addElementCall: function addElementCall (elementToolTip,elementName,elementValue,oobdElementFlags,optid,optTable) {
		console.log('addElementCall from Lua with optiontable:', optTable);
/* 
		try {
			String updevent = "";
			int oobdElementFlags = getInt(3);
			if (oobdElementFlags > 0) {
				updevent = "'" + FN_UPDATEOPS + "':" + oobdElementFlags
						+ ",";
			}
			String optid = getString(4); // String id
			// Android: String.isEmpty() not available
			// if (!optid.isEmpty()) {
			if (optid.length() != 0) {
				optid = "'optid':'" + optid + "',";
			}
			Onion myOnion = new Onion("" + "{'type':'" + CM_VISUALIZE + "',"
					+ "'owner':" + "{'name':'" + myself.getId()
					+ "'}," + updevent + optid + "'tooltip':'"
					+ Base64Coder.encodeString(getString(0))
					+ "'," + "'value':'"
					+ Base64Coder.encodeString(getString(2))
					+ "'," + "'name':'" + getString(1) + ":"
					+ getString(4) + "'}");
			Onion optTable = getLuaTable(5);
			if (optTable != null) {
				myOnion.setValue("opts", optTable);
			}
			core.transferMsg(new Message(myself, UIHandlerMailboxName,
					myOnion));

		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}

 */
		return 1;
	},

	pageDoneCall: function pageDoneCall () {
		console.log('pageDoneCall from Lua:');
/* 
		try {
			core.transferMsg(new Message(myself, UIHandlerMailboxName,
					new Onion("" + "{'type':'" + CM_PAGEDONE + "',"
							+ "'owner':'" + myself.getId() + "',"
							+ "'name':'Canvastest_1'}")));
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}

		// finishRPC(callFrame, nArguments);
 */
		return 1;
	},

	openChannelCall: function openChannelCall (connectURLParameter) {
		console.log('openChannelCall from Lua:');

		if (connectURLParameter != null && !"".equals(connectURLParameter)) {
			connectURL = Base64Coder.encodeString(connectURLParameter);
		}
/*				try {
			myself.getMsgPort().sendAndWait(
					new Message(myself, CoreMailboxName, new Onion(""
									+ "{'type':'" + CM_CHANNEL + "'"
									+ ",'owner':'" + myself.getId() + "'"
									+ ",'command':'connect'"
									+ ",'connecturl':'" + connectURL + "'" //just as reminder : connectURL comes already base64 coded
									+ "}")), -1);
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}

*/
		return 1;
	},

	dbLookupCall: function dbLookupCall () {
		console.log('dbLookupCall from Lua:');

/* 
		Onion result = new Onion();
		Message answer = null;
		try {
			answer = myself.getMsgPort().sendAndWait(
					new Message(myself, DBName, new Onion(""
									+ "{'type':'"
									+ CM_DBLOOKUP
									+ "',"
									+ "'owner':"
									+ "{'name':'"
									+ myself.getId()
									+ "'},"
									+ "'command':'lookup',"
									+ "'dbfilename':'"
									+ Base64Coder.encodeString(
											//                                                    scriptDir +
											//                                                    "/" + 
											getString(0)
									)
									+ "',"
									// + "'dbfilename':'" + getString(0) + "',"
									+ "'key':'"
									+ Base64Coder.encodeString(getString(1))
									+ "'}")), -1);
			if (answer != null) {
				result = answer.getContent().getOnion("result");
			}
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}

		LuaTableImpl newTable = new LuaTableImpl();
		newTable = onion2Lua(result);
		callFrame.push(newTable);
 */
		return 1;
		

	},

	serFlushCall: function serFlushCall () {
		console.log('serFlushCall from Lua:');

/*
 		try {
			core.transferMsg(new Message(myself, BusMailboxName,
					new Onion("" + "{'type':'" + CM_BUSTEST + "',"
							+ "'owner':" + "{'name':'" + myself.getId()
							+ "'}," + "'command':'serFlush'}")));
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}
*/
		return 1;
	},

	serWriteCall: function serWriteCall ( message) {
		console.log('serWriteCall from Lua: ',  message);
		writeToStream(message)
/* 
		try {
			core.transferMsg(new Message(myself, BusMailboxName,
					new Onion("{" + "'type':'" + CM_BUSTEST + "',"
							+ "'owner':" + "{'name':'" + myself.getId()
							+ "'}," + "'command':'serWrite',"
							+ "'data':'"
							+ Base64Coder.encodeString(getString(0))
							+ "'" + "}")));
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}
 */
		return 1;
	},

	serWaitCall: function serWaitCall (time, message) {
		console.log('serWaitCall from Lua: ', time, message);
		var result = 0;
		if (message != null) { // send only if string contains
			// anything to wait for
			writeToStream(message)

/* 
			// BaseLib.luaAssert(nArguments >0, "not enough args");
			Message answer = null;
			try {
				answer = myself.getMsgPort().sendAndWait(
						new Message(
								myself,
								BusMailboxName,
								new Onion(
										""
										+ "{'type':'"
										+ CM_BUSTEST
										+ "',"
										+ "'owner':"
										+ "{'name':'"
										+ myself.getId()
										+ "'},"
										+ "'command':'serWait',"
										+ "'timeout':'"
										+ getInt(1)
										+ "',"
										+ "'data':'"
										+ Base64Coder.encodeString(message)
										+ "'}")),
						+(getInt(1) * 12) / 10);
				if (answer != null) {
					Logger.getLogger(ScriptengineLua.class.getName()).log(Level.INFO,
							"Lua calls serWait returns with onion:"
							+ answer.getContent().toString());
					result = answer.getContent().getInt("result");

				}

			} catch (JSONException ex) {
				Logger.getLogger(ScriptengineLua.class.getName()).log(
						Level.SEVERE, null, ex);
			}
 */
		}

		return result;
},

	serReadLnCall: function serReadLnCall (timeOut) {
		console.log('serReadLnCall from Lua:');

	/* 	String result = "";
		Message answer = null;
		try {
			answer = myself.getMsgPort().sendAndWait(
					new Message(myself, BusMailboxName, new Onion(""
									+ "{'type':'" + CM_BUSTEST + "',"
									+ "'owner':" + "{'name':'" + myself.getId()
									+ "'}," + "'command':'serReadLn',"
									+ "'timeout':'" + getInt(0) + "',"
									+ "'ignore':'"
									+ Boolean.toString(getBoolean(1)) + "'}")),
					+(getInt(0) * 12) / 10);
			if (answer != null) {
				result = answer.getContent().getString("result");
				if (result != null && result.length() > 0) {
					result = new String(Base64Coder.decodeString(result));
				}
				// } catch (IOException ex) {
				// Logger.getLogger(ScriptengineLua.class.getName()).log(Level.SEVERE,
				// null, ex);
				// }
			}
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}
		callFrame.push(result.intern());
		finishRPC(callFrame, nArguments);
	*/
		var result='';
		return result;
	},

	serDisplayWriteCall: function serDisplayWriteCall () {
		console.log('serDisplayWriteCall from Lua:');

/*
		try {

			String msg = "{" + "'type':'" + CM_WRITESTRING + "',"
					+ "'owner':" + "{'name':'" + myself.getId()
					+ "'}," + "'command':'serDisplayWrite',"
					+ "'data':'"
					+ Base64Coder.encodeString(getString(0))
					+ "'";
			String cmd = getString(1);
			if (cmd != null) {
				msg = msg + " , 'modifier':'"
						+ Base64Coder.encodeString(cmd)
						+ "'";
			}
			msg = msg + "}";
			core.transferMsg(new Message(myself, UIHandlerMailboxName,
					new Onion(msg)));

		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}
 */
		return 1;
},

	openXCVehicleDataCall: function openXCVehicleDataCall () {
		console.log('openXCVehicleDataCall from Lua:');
/*
		initRPC(callFrame, nArguments);
		Onion openXCJson = getLuaTable(0);
		if (openXCJson != null) {
			core.getSystemIF().openXCVehicleData(openXCJson);
		}
 */
		return 1;
   },

	serSleepCall: function serSleepCall (delayms) {
		console.log('serSleepCall from Lua:',delayms);
	},

	ioInputCall: function ioInputCall () {
		console.log('ioInputCall from Lua:');
/* 
		String potentialJSONParam;
		Onion optTable = null;
		Logger.getLogger(ScriptengineLua.class.getName()).log(
				Level.INFO,
				"Lua calls ioInputCall with string data:>" + getString(0)
				+ "<");
		try {
			optTable = getLuaTable(1);
		} catch (ClassCastException ex) {
			optTable = null;
		}
		if (optTable != null) {
			potentialJSONParam = optTable.toString();
		} else {
			potentialJSONParam = getString(1);
		}

		String result = createInputTempFile(getString(0), potentialJSONParam, getString(2));
		callFrame.push(result.intern());
 */
		return 1;
	},

	ioReadCall: function ioReadCall () {
		console.log('ioReadCall from Lua:');

/* 
		Logger.getLogger(ScriptengineLua.class.getName()).log(
				Level.INFO,
				"Lua calls ioReadCall with string data:>" + getString(0)
				+ "<");

		String result = readTempInputFile(getString(0));

		if ("*json".equalsIgnoreCase(getString(0))) {
			Onion answer = null;
			try {
				answer = new Onion(result);
			} catch (JSONException ex) {
				Logger.getLogger(ScriptengineLua.class.getName()).log(
						Level.SEVERE, null, ex);
			}

			LuaTableImpl newTable = new LuaTableImpl();
			newTable = onion2Lua(answer);
			callFrame.push(newTable);
		} else {
			if (result == null) {
				callFrame.push(null);
			} else {
				callFrame.push(result.intern());
			}
		}
 */
		return 1;


	},

	ioWriteCall: function ioWriteCall () {
		console.log('ioWriteCall from Lua:');
	},

	onionMsgCall: function onionMsgCall () {
		console.log('onionMsgCall from Lua:');
/* 
		Onion result = new Onion();
		Message answer = null;
		try {
			answer = myself.getMsgPort().sendAndWait(
					new Message(myself, DBName, new Onion(""
									+ "{'type':'"
									+ CM_DBLOOKUP
									+ "',"
									+ "'owner':"
									+ "{'name':'"
									+ myself.getId()
									+ "'},"
									+ "'command':'lookup',"
									+ "'dbfilename':'"
									+ Base64Coder.encodeString(scriptDir
											+ getString(0))
									+ "'," + "'key':'" + getString(1) + "'}")),
					-1);
			if (answer != null) {
				result = answer.getContent().getOnion("result");
			}
		} catch (JSONException ex) {
			Logger.getLogger(ScriptengineLua.class.getName()).log(
					Level.SEVERE, null, ex);
		}

		LuaTableImpl newTable = new LuaTableImpl();
		newTable = onion2Lua(result);
		callFrame.push(newTable);
 */
		return 1;

	},

	msgBoxCall: function msgBoxCall () {
		console.log('msgBoxCall from Lua:');
		var result = "";
/* 
		String typeOfBox = getString(0).toLowerCase();
		if ("alert".equals(typeOfBox)) {
			core.userAlert(getString(2), getString(1));
		} else {
			try {
				String msg = "{'" + CM_PARAM + "' : { "
						+ "'type':'String'," + "'title':'"
						+ Base64Coder.encodeString(getString(1))
						+ "'," + "'default':'"
						+ Base64Coder.encodeString(getString(3))
						+ "',"
						+ "'text':'"
						+ Base64Coder.encodeString(getString(2))
						+ "'";
				if ("confirm".equals(typeOfBox)) {
					msg = msg + " , 'confirm':'yes'";
				}
				msg = msg + "}}";
				Onion answer = core.requestParamInput(myself, new Onion(msg));
				Onion answerOnion = answer.getOnion("answer");
				if (answerOnion != null) {
					result = answerOnion.getString("answer");
					if (result != null && result.length() > 0) {
						result = Base64Coder.decodeString(result);
					}
				}
			} catch (JSONException ex) {
				Logger.getLogger(ScriptengineLua.class.getName()).log(
						Level.SEVERE, null, ex);
			}
		}
		callFrame.push(result.intern());
 */
		return result;
	},



};
