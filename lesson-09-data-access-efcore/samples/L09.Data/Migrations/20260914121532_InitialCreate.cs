using System;
using Microsoft.EntityFrameworkCore.Migrations;

#nullable disable

namespace L09.Data.Migrations
{
    /// <inheritdoc />
    public partial class InitialCreate : Migration
    {
        /// <inheritdoc />
        protected override void Up(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.CreateTable(
                name: "Vehicles",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    Make = table.Column<string>(type: "TEXT", maxLength: 40, nullable: false),
                    Model = table.Column<string>(type: "TEXT", maxLength: 40, nullable: false),
                    Year = table.Column<int>(type: "INTEGER", nullable: false),
                    EngineCc = table.Column<int>(type: "INTEGER", nullable: false),
                    Use = table.Column<string>(type: "TEXT", maxLength: 10, nullable: false),
                    SumInsured_Amount = table.Column<decimal>(type: "TEXT", precision: 12, scale: 2, nullable: false),
                    SumInsured_Currency = table.Column<string>(type: "TEXT", maxLength: 3, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Vehicles", x => x.Id);
                });

#region create-quotes
            migrationBuilder.CreateTable(
                name: "Quotes",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    Reference = table.Column<string>(type: "TEXT", maxLength: 12, nullable: false),
                    VehicleId = table.Column<int>(type: "INTEGER", nullable: false),
                    Coverage = table.Column<string>(type: "TEXT", maxLength: 12, nullable: false),
                    Status = table.Column<string>(type: "TEXT", maxLength: 10, nullable: false),
                    ValidUntil = table.Column<DateOnly>(type: "TEXT", nullable: false),
                    Version = table.Column<Guid>(type: "TEXT", nullable: false),
                    Driver_ClaimsLast5Years = table.Column<int>(type: "INTEGER", nullable: false),
                    Driver_DateOfBirth = table.Column<DateOnly>(type: "TEXT", nullable: false),
                    Driver_LicenceYears = table.Column<int>(type: "INTEGER", nullable: false),
                    Total_Amount = table.Column<decimal>(
                        type: "TEXT", precision: 12, scale: 2, nullable: false),
                    Total_Currency = table.Column<string>(type: "TEXT", maxLength: 3, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Quotes", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Quotes_Vehicles_VehicleId",
                        column: x => x.VehicleId,
                        principalTable: "Vehicles",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Restrict);
                });
#endregion

            migrationBuilder.CreateTable(
                name: "Policies",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    PolicyNumber = table.Column<string>(type: "TEXT", maxLength: 12, nullable: false),
                    QuoteId = table.Column<int>(type: "INTEGER", nullable: false),
                    Inception = table.Column<DateOnly>(type: "TEXT", nullable: false),
                    Expiry = table.Column<DateOnly>(type: "TEXT", nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_Policies", x => x.Id);
                    table.ForeignKey(
                        name: "FK_Policies_Quotes_QuoteId",
                        column: x => x.QuoteId,
                        principalTable: "Quotes",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateTable(
                name: "PremiumLines",
                columns: table => new
                {
                    Id = table.Column<int>(type: "INTEGER", nullable: false)
                        .Annotation("Sqlite:Autoincrement", true),
                    QuoteId = table.Column<int>(type: "INTEGER", nullable: false),
                    Kind = table.Column<string>(type: "TEXT", maxLength: 16, nullable: false),
                    Amount_Amount = table.Column<decimal>(type: "TEXT", precision: 12, scale: 2, nullable: false),
                    Amount_Currency = table.Column<string>(type: "TEXT", maxLength: 3, nullable: false)
                },
                constraints: table =>
                {
                    table.PrimaryKey("PK_PremiumLines", x => x.Id);
                    table.ForeignKey(
                        name: "FK_PremiumLines_Quotes_QuoteId",
                        column: x => x.QuoteId,
                        principalTable: "Quotes",
                        principalColumn: "Id",
                        onDelete: ReferentialAction.Cascade);
                });

            migrationBuilder.CreateIndex(
                name: "IX_Policies_PolicyNumber",
                table: "Policies",
                column: "PolicyNumber",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Policies_QuoteId",
                table: "Policies",
                column: "QuoteId",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_PremiumLines_QuoteId",
                table: "PremiumLines",
                column: "QuoteId");

            migrationBuilder.CreateIndex(
                name: "IX_Quotes_Reference",
                table: "Quotes",
                column: "Reference",
                unique: true);

            migrationBuilder.CreateIndex(
                name: "IX_Quotes_VehicleId",
                table: "Quotes",
                column: "VehicleId");
        }

        /// <inheritdoc />
        protected override void Down(MigrationBuilder migrationBuilder)
        {
            migrationBuilder.DropTable(
                name: "Policies");

            migrationBuilder.DropTable(
                name: "PremiumLines");

            migrationBuilder.DropTable(
                name: "Quotes");

            migrationBuilder.DropTable(
                name: "Vehicles");
        }
    }
}
