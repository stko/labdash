var readyStateCheckInterval = setInterval(function () {
	if (document.readyState === "complete") {
		clearInterval(readyStateCheckInterval);
		Eol.init();
		// Get all elements, which are defined as eol class
	}
}, 10);



/**
 * Eol namespace.
 */
if (typeof Eol == "undefined") {
	Eol = {
		/**
		 * Initializes this object.
		 */
		wsURL: "ws://" + window.location.hostname + ":" + window.location.port + '/ws',
		alreadyInitialized: false,
		session: null,
		connection: "",
		scriptID: "",
		updateNormalMarker: false,
		updateTimerMarker: false,
		timerFlag: -1,
		timerObject: null,
		visualizers: new Array(),
		parseXml: null,
		fileSystem: null,
		onInitFs: null,
		onInitFserrorHandler: null,
		bufferName: "display",
		fsBufferArray: new Object(),
		fsBufferCounter: 0,
		isTouchDevice: 'ontouchstart' in document.documentElement,
		uniqueID: 0,
		getUniqueID: function () {
			try {
				Eol.uniqueID++;
			} catch (ex) {
				Eol.uniqueID = 0;
			}
			return Eol.uniqueID;
		},

		loadSession: function () {
			if (Eol.session == null) {
				Eol.session = JSON.parse(localStorage.getItem('session'));
			};
			if (Eol.session == null) {
				Eol.session = {
					dashboard: [],
					connectType: "",
					pgpid: "",
					theme: "",
					connectID: {}
				}
			}
		},

		loadUserPrefs: function (connectTypeSelect, pgpidInput, themeSelect, connectIDInput) {
			Eol.loadSession();
			if (Eol.session.connectType != "") {
				connectTypeSelect.value = Eol.session.connectType;
			}
			if (Eol.session.pgpid != "") {
				pgpidInput.value = Eol.session.pgpid;
			}
			if (Eol.session.theme != "") {
				themeSelect.value = Eol.session.theme;
			}
			if (typeof Eol.session.connectID[Eol.session.connectType] != "undefined" && Eol.session.connectID[Eol.session.connectType] != "") {
				connectIDInput.value = Eol.session.connectID[Eol.session.connectType];
			}
		},

		saveUserPrefs: function (connectTypeSelect, pgpidInput, themeSelect, connectIDInput) {
			Eol.session.connectType = connectTypeSelect.value;
			Eol.session.pgpid = pgpidInput.value;
			Eol.session.theme = themeSelect.value;
			Eol.session.connectID[Eol.session.connectType] = connectIDInput.value;
			localStorage.setItem('session', JSON.stringify(Eol.session));
		},

		init: function (uri) {
			if (Eol.alreadyInitialized) {
				return;
			}
			Eol.alreadyInitialized = true;
			// preparing utility funktion parse xmlDoc
			if (window.DOMParser) {
				this.parseXml = function (xmlStr) {
					return (new window.DOMParser()).parseFromString(xmlStr, "text/xml");
				};
			} else if (typeof window.ActiveXObject != "undefined" && new window.ActiveXObject("Microsoft.XMLDOM")) {
				this.parseXmlparseXml = function (xmlStr) {
					var xmlDoc = new window.ActiveXObject("Microsoft.XMLDOM");
					xmlDoc.async = "false";
					xmlDoc.loadXML(xmlStr);
					return xmlDoc;
				};
			} else {
				this.parseXmlparseXml = function () {
					return null;
				}
			}
			// try to disconnect the websocket as much early as possible before the new page is loaded
			window.addEventListener("unload", function () {
				/*Send a small message to the console once the connection is established */
				console.log('try to close Websocket');
				if (typeof Eol.connection != "undefined") {
					Eol.connection.close();
					console.log('Websocket closed');

				}
			});

			// try to init the file system
			Eol.onInitFs = function onInitFs(fs) {
				console.log('Opened file system: ' + fs.name);
				Eol.fileSystem = fs;
			};
			Eol.onInitFserrorHandler = function errorHandler(e) {
				console.log('FileSystem ' + e.name + '  ' + e.message);
			}
			// trying to be compatible
			window.URL = window.URL || window.webkitURL;
			window.resolveLocalFileSystemURL = window.resolveLocalFileSystemURL || window.webkitResolveLocalFileSystemURL || window.resolveLocalFileSystemURI;
			window.BlobBuilder = window.WebKitBlobBuilder || window.MozBlobBuilder || window.BlobBuilder;
			window.requestFileSystem = window.requestFileSystem || window.webkitRequestFileSystem;
			window.requestFileSystem(window.TEMPORARY, 5 * 1024 * 1024 /*5MB*/, Eol.onInitFs, Eol.onInitFserrorHandler);
			Eol.loadSession();
		},

		_announceFileChange: function (id, url, change) {
			console.log("Announce File change: " + change + " for id " + id + " with URL " + url);
			if (typeof Eol.fileChange != "undefined") {
				Eol.fileChange(id, url, change);
			}
		},

		_handleWriteString: function (msg) {
			var data = "";
			var modifier = "";
			if (typeof msg.modifier != "undefined" && msg.modifier.length > 0) {
				modifier = msg.modifier.toLowerCase();
			}
			if (typeof msg.data != "undefined" && msg.data.length > 0) {
				data = msg.data;
			}
			console.log("File handler called with modifier >" + modifier + "< and data >" + data + "<");
			switch (modifier) {
				case "setbuffer":
					Eol.bufferName = data.toLowerCase();
					break;
				case "save":
				case "saveas":
					if (Eol.bufferName == "display") { // a normal writestring
						if (typeof Eol.writeString != "undefined") {
							console.log("try to WRITESTRING");
							console.log(msg);
							Eol.writeString(data, "save");
						}
					} else { // savefile
						if (typeof Eol.fileSystem != "undefined") {
							//do we have the actual buffer already?
							var actBufferIndex = Eol.fsBufferArray[Eol.bufferName];
							if (typeof actBufferIndex != "undefined") {
								Eol.fileSystem.root.getFile(actBufferIndex, { create: false }, function (fileEntry) {
									console.log('Try to download' + fileEntry.toURL());
									var a = document.createElement('a');
									a.download = data;
									a.href = fileEntry.toURL();
									a.textContent = "Save: " + Eol.bufferName;
									a.click();

								}, Eol.onInitFserrorHandler);
							}
						}
					}
					break;
				case "close":
					if (Eol.bufferName != "display") { // a normal writestring
						if (typeof Eol.fileSystem != "undefined") {
							//do we have the actual buffer already?
							var thisBufferName = Eol.bufferName;
							var actBufferIndex = Eol.fsBufferArray[Eol.bufferName];
							if (typeof actBufferIndex != "undefined") {
								console.log("try to close file " + thisBufferName);
								Eol.fileSystem.root.getFile(actBufferIndex, { create: false }, function (fileEntry) {
									Eol._announceFileChange(thisBufferName, fileEntry.toURL(), "close");

								}, Eol.onInitFserrorHandler);
							}
						}
					}
					break;
				case "clear":
					if (Eol.bufferName == "display") { // a normal writestring
						if (typeof Eol.writeString != "undefined") {
							console.log("try to WRITESTRING");
							console.log(msg);
							Eol.writeString(data, "cLlear");
						}
					} else { // delete
						if (typeof Eol.fileSystem != "undefined") {
							//do we have the actual buffer already?
							var thisBufferName = Eol.bufferName;
							var actBufferIndex = Eol.fsBufferArray[thisBufferName];
							if (typeof actBufferIndex != "undefined") {
								Eol.fileSystem.root.getFile(actBufferIndex, { create: true }, function (fileEntry) {
									console.log('Try delete buffer ' + thisBufferName + " with index " + fileEntry.name);
									fileEntry.remove(function () {
										console.log('File removed:' + Eol.bufferName + "/" + thisBufferName);
										delete Eol.fsBufferArray[thisBufferName];
										Eol._announceFileChange(thisBufferName, "", "clear");
									}, Eol.onInitFserrorHandler);

								}, Eol.onInitFserrorHandler);
							}
						}
					}
					break;
				default:
					if (typeof data != "undefined" && data.length > 0) {
						if (Eol.bufferName == "display") { // a normal writestring
							if (typeof Eol.writeString != "undefined") {
								console.log("try to WRITESTRING");
								console.log(msg);
								Eol.writeString(data + "\n", "");
							}
						} else { // writetofile
							console.log("WRITESTRING modifier " + modifier);
							if (typeof Eol.fileSystem != "undefined") {
								//do we have the actual buffer already?
								var thisBufferName = Eol.bufferName;
								var actBufferIndex = Eol.fsBufferArray[thisBufferName];
								var isNewfile = false;
								if (typeof actBufferIndex == "undefined") {
									actBufferIndex = Eol.fsBufferCounter++;
									Eol.fsBufferArray[thisBufferName] = actBufferIndex;
									console.log('new Buffer "' + thisBufferName + '" created with index:' + actBufferIndex);
									isNewfile = true;
								}
								console.log("try to write to a file with bufferindex " + actBufferIndex);
								Eol.fileSystem.root.getFile(actBufferIndex, { create: true }, function (fileEntry) {

									// Create a FileWriter object for our FileEntry (log.txt).
									fileEntry.createWriter(function (fileWriter) {
										fileWriter.fe = fileEntry;
										fileWriter.onwriteend = function (e) {
											var src = e.target.fe.toURL();
											var src2 = fileEntry.toURL();
											console.log('Write completed with URL' + src2);
										};

										fileWriter.onerror = function (e) {
											console.log('Write failed on bufferindex ' + actBufferIndex + ': ' + e.toString());
										};
										console.log("FileWriter.length=", fileWriter.length);
										if (isNewfile) { // new file
											isNewfile = false;
											Eol._announceFileChange(thisBufferName, fileEntry.toURL(), "create");
										}
										fileWriter.seek(fileWriter.length); // Start write position at EOF.
										// Create a new Blob and write it to log.txt.
										window.BlobBuilder = window.BlobBuilder || window.WebKitBlobBuilder;// Note: window.WebKitBlobBuilder in Chrome 12.
										var blob = new Blob([data], { type: 'application/octet-stream' });
										fileWriter.write(blob);
									}, Eol.onInitFserrorHandler);
								}, Eol.onInitFserrorHandler);
							}
						}
					}
			}



		},

		start: function (webSocketURL) {
			if ('WebSocket' in window) {
				/* WebSocket is supported. You can proceed with your code*/
				if (typeof webSocketURL == "undefined") {
					webSocketURL = this.wsURL;
				}
				this.connection = new WebSocket(webSocketURL);
				this.connection.onopen = function () {
					/*Send a small message to the console once the connection is established */
					console.log('Connection open!');
				}

				this.connection.onclose = function () {
					console.log('Connection closed');
				}

				this.connection.onmessage = function (rawMsg) {
					console.log("data " + rawMsg.data); // this is the full message
					try {
						var obj = JSON.parse(rawMsg.data);
						if (obj.type == "EOLLIST") {
							Eol.newList(obj.config.title)
							obj.config.items.forEach(element => Eol.addListElement(element))
							Eol.listDone()
						}

						if (obj.type == "WSCONNECT") {
							Eol.scriptID = obj.config.script;
							if (typeof Eol.onConnect != "undefined") {
								Eol.onConnect();
							}
						}

						if (obj.type == "WRITESTRING") {
							Eol._handleWriteString(obj.config);
						}

						if (obj.type == "PARAM") {
							if (typeof obj.config.PARAM.confirm != "undefined") { // do we need a yes/no dialog or a value input?
								if (typeof Eol.confirm != "undefined") {
									console.log("try to open confirm");
									Eol.confirm(obj.config);
								} else {
									var answer = window.confirm(obj.config.PARAM.text) ? "true" : "false";
									Eol.connection.send(JSON.stringify({ "type": "PARAM", "answer": answer }));
								}
							} else {
								if (typeof Eol.prompt != "undefined") {
									console.log("try to open prompt");
									Eol.prompt(obj.config);
								} else {
									var answer = window.prompt(obj.config.PARAM.text, obj.config.PARAM.default);
									Eol.connection.send(JSON.stringify({ "type": "PARAM", "answer": answer }));
								}
							}
						}
						if (obj.type == "DIALOG_INFO") {
							if (typeof Eol.alert != "undefined") {
								console.log("try to open Alert");
								Eol.alert(obj.config);
							} else {
								window.alert(obj.config.DIALOG_INFO.tooltip);
							}
						}
						if (obj.type == "ICONSTATES" && Eol.setIconStates) {
							Eol.setIconStates(obj.config);
						}

					} catch (err) {
						console.log("received msg Error " + err.message);
					}
				}
			} else {
				window.alert("Socket not supported");
			}
		},

		parseXml: function (xmlText) {
			if (window.DOMParser) {
				parser = new DOMParser();
				xmlDoc = parser.parseFromString(xmlText, "text/xml");
				return xmlDoc;
			}
			else // Internet Explorer
			{
				xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
				xmlDoc.async = false;
				xmlDoc.loadXML(xmlText);
				return xmlDoc;
			}
		},

		loadXML: function (path, callback) {
			var request;

			// Create a request object. Try Mozilla / Safari method first.
			if (window.XMLHttpRequest) {
				request = new XMLHttpRequest();

				// If that doesn't work, try IE methods.
			} else if (window.ActiveXObject) {
				try {
					request = new ActiveXObject("Msxml2.XMLHTTP");
				} catch (e1) {
					try {
						request = new ActiveXObject("Microsoft.XMLHTTP");
					} catch (e2) { }
				}
			}

			// If we couldn't make one, abort.
			if (!request) {
				return;
			}

			// Upon completion of the request, execute the callback.
			request.onreadystatechange = function () {
				if (request.readyState === 4) {
					if (request.status === 200) {
						callback(request.responseText);
					}
				}
			};

			request.open("GET", path);
			try {
				req.responseType = "msxml-document"
			} catch (ex) { }
			request.send();
		},

		createXsltTransformer: function (path, callback) {

			Eol.loadXML(path, function (xslText) {
				// xml contains the desired xml document.
				// do something useful with it!
				var xsl = Eol.parseXml(xslText);

				// code for Chrome, Firefox, Opera, etc.
				if (document.implementation && document.implementation.createDocument) {
					var xsltProcessor = new XSLTProcessor();
					xsltProcessor.importStylesheet(xsl);
					callback(xsltProcessor);
				}
			});
		},

		sendUpdateReq: function (name, optid, value, updType) {
			if (typeof Eol.connection.send != "undefined") {
				Eol.connection.send(JSON.stringify({ "name": name, "optid": optid, "actValue": value, "updType": updType }));
			} else {
				return false;
			}
		},

		rewind_request(){
			if (typeof Eol.connection.send != "undefined") {
				Eol.connection.send(JSON.stringify({ "type": "REWINDREQUEST", }));
			} else {
				return false;
			}
		},

		play_request(selected_node,checked_nodes){
			if (typeof Eol.connection.send != "undefined") {
				Eol.connection.send(JSON.stringify({ "type": "PLAYREQUEST", "selected_node": selected_node, "checked_nodes": checked_nodes }));
			} else {
				return false;
			}
		},

		stop_request(){
			if (typeof Eol.connection.send != "undefined") {
				Eol.connection.send(JSON.stringify({ "type": "stoprequest" }));
			} else {
				return false;
			}
		},
	}

}
