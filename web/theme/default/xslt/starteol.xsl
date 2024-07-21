<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

	<xsl:template match="/">
		<html>
			<head>
				<meta charset="utf-8" />
				<link rel="apple-touch-icon" sizes="57x57" href="/theme/default/favicon/apple-icon-57x57.png" />
				<link rel="apple-touch-icon" sizes="60x60" href="/theme/default/favicon/apple-icon-60x60.png" />
				<link rel="apple-touch-icon" sizes="72x72" href="/theme/default/favicon/apple-icon-72x72.png" />
				<link rel="apple-touch-icon" sizes="76x76" href="/theme/default/favicon/apple-icon-76x76.png" />
				<link rel="apple-touch-icon" sizes="114x114" href="/theme/default/favicon/apple-icon-114x114.png" />
				<link rel="apple-touch-icon" sizes="120x120" href="/theme/default/favicon/apple-icon-120x120.png" />
				<link rel="apple-touch-icon" sizes="144x144" href="/theme/default/favicon/apple-icon-144x144.png" />
				<link rel="apple-touch-icon" sizes="152x152" href="/theme/default/favicon/apple-icon-152x152.png" />
				<link rel="apple-touch-icon" sizes="180x180" href="/theme/default/favicon/apple-icon-180x180.png" />
				<link rel="icon" type="image/png" sizes="192x192" href="/theme/default/favicon/android-icon-192x192.png" />
				<link rel="icon" type="image/png" sizes="32x32" href="/theme/default/favicon/favicon-32x32.png" />
				<link rel="icon" type="image/png" sizes="96x96" href="/theme/default/favicon/favicon-96x96.png" />
				<link rel="icon" type="image/png" sizes="16x16" href="/theme/default/favicon/favicon-16x16.png" />
				<link rel="manifest" href="/theme/default/favicon/manifest.json" />
				<meta name="msapplication-TileColor" content="#ffffff" />
				<meta name="msapplication-TileImage" content="/theme/default/favicon/ms-icon-144x144.png" />
				<meta name="theme-color" content="#ffffff" />
				<title>EOL Main Page</title>
				<!--meta name="viewport" content="width=device-width, initial-scale=1"-->
				<!--meta name="viewport" content="width=device-width, initial-scale=1"-->
				<link rel="stylesheet" href="/libs/jquery-ui-themes/1.11.4/themes/dark-hive/jquery-ui.css" />
				<link rel="stylesheet" href="/libs/jquery-ui-themes/1.11.4/themes/dark-hive/theme.css" />


				<script src="/libs/jquery/2.1.4/jquery.min.js"></script>
				<script src="/libs/jquery-ui/1.11.4/jquery-ui.js"></script>

				<link rel="stylesheet" href="/libs/jqwidgets/3.8.2/styles/jqx.base.css" type="text/css" />
				<script type="text/javascript" src="/libs/jqwidgets/3.8.2/jqxcore.js"></script>
				<script type="text/javascript" src="/libs/jqwidgets/3.8.2/jqxchart.js"></script>
				<script type="text/javascript" src="/libs/jqwidgets/3.8.2/jqxgauge.js"></script>

				<meta content="initial-scale=1.0, maximum-scale=1.0, user-scalable=no" name="viewport" />
				<meta name="msapplication-tap-highlight" content="no" />
				<link rel="stylesheet" type="text/css" href="/theme/default/css/style.css" />
				<script type="text/javascript" src="/libs/oobd/1/eol.js"></script>

				<script>
		$(function() {
			$("#prefbutton").button({
				icons: {
					primary: "ui-icon-gear"
				}
			});
			$("#tabs").tabs();
			$("#accordion").accordion();
			$("#theme").selectmenu();
			$("#pgppw").button();
			$("#rcid").button();
			$("#connectType").selectmenu();
			$("#submitbuton").button();
			$("#radioset").buttonset();
			$("#dialog").dialog({
				autoOpen: false,
				width: 400,
				buttons: [{
					text: "Ok",
					click: function() {
						$(this).dialog("close");
					}
				}, {
					text: "Cancel",
					click: function() {
						$(this).dialog("close");
					}
				}]
			});
			// Link to open the dialog
			$("#dialog-link").click(function(event) {
				$("#dialog").dialog("open");
				event.preventDefault();
			});
			$("#datepicker").datepicker({
				inline: true
			});
			$("#progressbar").progressbar({
				value: 20
			});
			$("#spinner").spinner();
			$("#menu").menu();
			$("#tooltip").tooltip();
			$("#selectmenu").selectmenu();
			// Hover states on the static widgets
			$("#dialog-link, #icons li").hover(
				function() {
					$(this).addClass("ui-state-hover");
				},
				function() {
					$(this).removeClass("ui-state-hover");
				}
			);
		});
				</script>
				<style>
.grid-container {
  display: grid;
  grid-template-columns: auto auto auto;
  //background-color: #2196F3;
  padding: 10px;
}
.grid-item {
  background-color: rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.8);
  padding: 20px;
  font-size: 30px;
  text-align: center;
}
				</style>
			</head>
			<body>
				<h2>
					<a target="_blank" href="http://oobd.org">
						<img src="/libs/images/oobd_logo_tron.png" width="100"/>
					</a>
					<!-- <h2><xsl:value-of select="catalog/title"/></h2> -->
					<!--xsl:for-each select="catalog" -->
					<xsl:choose>
						<xsl:when test="catalog/title !=''">
							<xsl:value-of select="catalog/title"/>
						</xsl:when>
						<xsl:otherwise>
				OOBD - Open Onboard Diagnostics
						</xsl:otherwise>
					</xsl:choose>
					<!-- /xsl:for-each-->
				</h2>
				<div id="toolbar" class="ui-widget-header ui-corner-all">
					<form action="#" method="post" id="form_2">
						<button id="prefbutton" onclick="window.location = '/theme/default/settings.html';return false;">Settings</button>

						<label for="theme">UI Theme</label>
						<select name="theme" id="theme" size="1">
							<xsl:for-each select="catalog/theme">
								<xsl:choose>
									<xsl:when test="@selected">
										<option selected="selected">
											<xsl:value-of select="."/>
										</option>
									</xsl:when>
									<xsl:otherwise>
										<option>
											<xsl:value-of select="."/>
										</option>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:for-each>
						</select>
						<label for="pgppw">PGP passphrase</label>
						<input type="text" name="pgppw" id="pgppw" maxlength="30"/>

						<label for="rcid">Remote Connect ID</label>
						<input type="text" name="rcid" id="rcid" maxlength="40"/>
						<label for="connectType">Connection Type</label>
						<select name="connectType" id="connectType" size="1">
							<xsl:for-each select="catalog/connection">
								<xsl:choose>
									<xsl:when test="@selected">
										<option selected="selected">
											<xsl:value-of select="."/>
										</option>
									</xsl:when>
									<xsl:otherwise>
										<option>
											<xsl:value-of select="."/>
										</option>
									</xsl:otherwise>
								</xsl:choose>
							</xsl:for-each>
						</select>
						<button type="submit" id="submitbuton" onclick="setPrefs()">Set</button>
					</form>
				</div>

				<div class="grid-container">
					<xsl:for-each select="catalog/script">
						<div>
							<table class="oobd-script-table">
								<xsl:choose>

									<xsl:when test="icon !=''">
										<tr class="oobd-script-icon-tr">
											<td colspan="2">
												<a href="{fileid}">
													<img class="oobd-script-icon" src="{fileid}/{icon}"/>
												</a>
											</td>
										</tr>
									</xsl:when>
									<xsl:otherwise>
										<tr class="oobd-script-icon-tr">
											<td colspan="2">
												<a href="{fileid}">
													<img class="oobd-script-icon" src="/theme/default/images/oobd_button.svg"/>
												</a>
											</td>
										</tr>
									</xsl:otherwise>
								</xsl:choose>
								<tr class="oobd-script-filename-tr">
									<td colspan="2" class="oobd-script-filename">
										<xsl:choose>
											<xsl:when test="title !=''">
												<xsl:value-of select="title"/>
											</xsl:when>
											<xsl:otherwise>
												<xsl:value-of select="filename"/>
											</xsl:otherwise>
										</xsl:choose>
									</td>
								</tr>
								<xsl:choose>
									<xsl:when test="name !=''">
										<tr>
											<td>name</td>
											<td>
												<xsl:value-of select="name"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="shortname !=''">
										<tr>
											<td>shortname</td>
											<td>
												<xsl:value-of select="shortname"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="description !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-lightbulb"/>
											</td>
											<td>
												<xsl:value-of select="description" disable-output-escaping="yes" />
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="version !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-tag"/>
											</td>
											<td>
												<xsl:value-of select="version"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="copyright !=''">
										<tr>
											<td>&#169;</td>
											<td>
												<xsl:value-of select="copyright"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="author !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-person"/>
											</td>
											<td>
												<xsl:value-of select="author"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="security !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-key"/>
											</td>
											<td>
												<xsl:value-of select="security"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="date !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-calendar"/>
											</td>
											<td>
												<xsl:value-of select="date"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="url !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-home"/>
											</td>
											<td>
												<a href="http://{url}">
													<xsl:value-of select="url"/>
												</a>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="email !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-mail-closed"/>
											</td>
											<td>
												<a href="mailto://{email}">
													<xsl:value-of select="email"/>
												</a>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<xsl:choose>
									<xsl:when test="phone !=''">
										<tr>
											<td>
												<span class="ui-icon ui-icon-volume-on"/>
											</td>
											<td>
												<xsl:value-of select="phone"/>
											</td>
										</tr>
									</xsl:when>
								</xsl:choose>
								<tr class="oobd-script-screenshot-tr">
									<td colspan="2">
										<xsl:choose>
											<xsl:when test="screenshot !=''">
												<img class="oobd-script-screenshot" src="{fileid}/{screenshot}"/>
											</xsl:when>
										</xsl:choose>
									</td>
								</tr>
							</table>
						</div>
					</xsl:for-each>
				</div>


				<script type="text/javascript">
	$(document).ready(function(){
		// Do all the UI initialisatiin
	});
	Eol.loadUserPrefs(document.getElementById('connectType'),document.getElementById('pgppw'),document.getElementById('theme'),document.getElementById('rcid'));
	function setPrefs(){
		Eol.saveUserPrefs(document.getElementById('connectType'),document.getElementById('pgppw'),document.getElementById('theme'),document.getElementById('rcid'));
		return true;
	}
	// start the EOL handler
	//	Eol.start()
				</script>
			</body>
		</html>
	</xsl:template>

</xsl:stylesheet>