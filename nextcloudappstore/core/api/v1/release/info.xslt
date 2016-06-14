<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/info">
        <app>
            <!-- must have attributes -->
            <id><xsl:value-of select="id"/></id>
            <categories type="list">
                <xsl:for-each select="category">
                    <category>
                        <id><xsl:value-of select="."/></id>
                    </category>
                </xsl:for-each>
            </categories>

            <xsl:for-each select="description">
                <description type="l10n">
                    <value><xsl:value-of select="."/></value>
                    <xsl:choose>
                        <xsl:when test="@lang">
                            <lang><xsl:value-of select="."/></lang>
                        </xsl:when>
                        <xsl:otherwise>
                            <lang>en</lang>
                        </xsl:otherwise>
                    </xsl:choose>
                </description>
            </xsl:for-each>

            <xsl:for-each select="name">
                <name type="l10n">
                    <value><xsl:value-of select="."/></value>
                    <xsl:choose>
                        <xsl:when test="@lang">
                            <lang><xsl:value-of select="."/></lang>
                        </xsl:when>
                        <xsl:otherwise>
                            <lang>en</lang>
                        </xsl:otherwise>
                    </xsl:choose>
                </name>
            </xsl:for-each>

            <screenshots type="list">
                <xsl:for-each select="screenshot">
                    <screenshot>
                        <url><xsl:value-of select="."/></url>
                    </screenshot>
                </xsl:for-each>
            </screenshots>

            <!-- optional elements need defaults -->
            <user-docs><xsl:value-of select="documentation/user"/></user-docs>
            <admin-docs><xsl:value-of select="documentation/admin"/></admin-docs>
            <developer-docs><xsl:value-of select="documentation/developer"/></developer-docs>

            <website><xsl:value-of select="website"/></website>
            <issue-tracker><xsl:value-of select="bugs"/></issue-tracker>

            <!-- release -->
            <release>
                <version><xsl:value-of select="version"/></version>
                <authors type="list">
                    <xsl:for-each select="author">
                        <author>
                            <name><xsl:value-of select="."/></name>
                            <mail><xsl:value-of select="@mail"/></mail>
                            <homepage><xsl:value-of select="@homepage"/></homepage>
                        </author>
                    </xsl:for-each>
                </authors>
                <licenses type="list">
                    <xsl:for-each select="licence">
                        <license>
                            <id><xsl:value-of select="."/></id>
                        </license>
                    </xsl:for-each>
                </licenses>

                <xsl:apply-templates select="dependencies"/>
            </release>
        </app>
    </xsl:template>

    <xsl:template match="dependencies">
        <php-min-version><xsl:value-of select="php/@min-version"/></php-min-version>
        <php-max-version><xsl:value-of select="php/@max-version"/></php-max-version>
        <min-int-size><xsl:value-of select="php/@min-int-size"/></min-int-size>
        <platform-min-version><xsl:value-of select="owncloud/@min-version"/></platform-min-version>
        <platform-max-version><xsl:value-of select="owncloud/@max-version"/></platform-max-version>

        <php-extensions type="list">
            <php-extension-dependencies type="list">
                <xsl:for-each select="lib">
                    <php-extension-dependency>
                        <min-version><xsl:value-of select="@min-version"/></min-version>
                        <max-version><xsl:value-of select="@max-version"/></max-version>
                        <php-extension>
                            <id><xsl:value-of select="."/></id>
                        </php-extension>
                    </php-extension-dependency>
                </xsl:for-each>
            </php-extension-dependencies>
        </php-extensions>
        <databases type="list">
            <database-dependencies type="list">
                <xsl:for-each select="database">
                    <database-dependency>
                        <min-version><xsl:value-of select="@min-version"/></min-version>
                        <max-version><xsl:value-of select="@max-version"/></max-version>
                        <database>
                            <id><xsl:value-of select="."/></id>
                        </database>
                    </database-dependency>
                </xsl:for-each>
            </database-dependencies>
        </databases>
        <shell-commands type="list">
            <xsl:for-each select="command">
                <shell-command><xsl:value-of select="."/></shell-command>
            </xsl:for-each>
        </shell-commands>
    </xsl:template>
</xsl:stylesheet>
